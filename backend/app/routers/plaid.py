from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_transactions import LinkTokenTransactions
from fastapi import APIRouter
from app.services.plaid_service import client
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from pydantic import BaseModel
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest

from app.db.connection import SessionLocal
from sqlalchemy import text


router = APIRouter()
@router.post("/create-link-token")
def create_link_token():

    request = LinkTokenCreateRequest(
    user=LinkTokenCreateRequestUser(
        client_user_id='user-id'
    ),
    client_name='Personal Finance App',
    products=[Products('transactions')],
    transactions=LinkTokenTransactions(
        days_requested=730
    ),
    country_codes=[CountryCode('CA')],
    language='en',
    )
    # create link token
    response = client.link_token_create(request)
    link_token = response['link_token']
    # your code here
    return {"link_token": link_token}


@router.post("/sandbox/create-public-token")
def create_sandbox_public_token():
    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[Products("transactions")]
    )
    response = client.sandbox_public_token_create(request)
    return {"public_token": response["public_token"]}

class ExchangeTokenRequest(BaseModel):
    public_token: str

@router.post("/exchange-token")
def exchange_token(data: ExchangeTokenRequest):
    request = ItemPublicTokenExchangeRequest(public_token=data.public_token)
    response = client.item_public_token_exchange(request)
    
    access_token = response['access_token']
    item_id = response['item_id']
    
    # save to DB
    db = SessionLocal()
    try:
        db.execute(text("""
            INSERT INTO institutions (plaid_item_id, access_token, institution_id, institution_name)
            VALUES (:item_id, :access_token, :institution_id, :institution_name)
        """), {
            "item_id": item_id,
            "access_token": access_token,
            "institution_id": "ins_109508",  # You should replace this with the actual institution_id from the Plaid response
            "institution_name": "Chase"  # You should replace this with the actual institution_name from the Plaid response
        })
        db.commit()
    finally:
        db.close()
    
    return {"access_token": access_token, "item_id": item_id}


from plaid.model.accounts_get_request import AccountsGetRequest

@router.post("/sync-accounts")
def sync_accounts():
    db = SessionLocal()
    try:
        institution = db.execute(text(
            "SELECT id, access_token FROM institutions LIMIT 1"
        )).fetchone()

        request = AccountsGetRequest(access_token=institution.access_token)
        response = client.accounts_get(request)

        for account in response['accounts']:
            db.execute(text("""
                INSERT INTO accounts 
                    (institution_id, plaid_account_id, name, type, subtype, current_balance, available_balance)
                VALUES
                    (:inst_id, :plaid_id, :name, :type, :subtype, :current, :available)
                ON CONFLICT (plaid_account_id) DO NOTHING
            """), {
                "inst_id": str(institution.id),
                "plaid_id": account["account_id"],
                "name": account["name"],
                "type": str(account["type"]),
                "subtype": str(account["subtype"]),
                "current": account["balances"]["current"],
                "available": account["balances"]["available"]
            })

        db.commit()
        return {"synced_accounts": len(response['accounts'])}
    finally:
        db.close()


from plaid.model.transactions_sync_request import TransactionsSyncRequest

@router.post("/sync-transactions")
def sync_transactions():
    db = SessionLocal()
    try:
        # Step 1 - get access token from DB
        institution = db.execute(text(
            "SELECT id, access_token, cursor FROM institutions LIMIT 1"
        )).fetchone()

        # Step 2 - call Plaid sync
        request = TransactionsSyncRequest(
            access_token=institution.access_token,
            cursor=institution.cursor or ""
        )
        response = client.transactions_sync(request)
        transactions = response['added']

        # Step 3 - store each transaction
        for txn in transactions:
            db.execute(text("""
                INSERT INTO transactions 
                    (account_id, plaid_transaction_id, amount, merchant_name, raw_name, date, pending, payment_channel)
                VALUES
                    (
                        (SELECT id FROM accounts WHERE plaid_account_id = :account_id LIMIT 1),
                        :plaid_id, :amount, :merchant, :raw_name, :date, :pending, :channel
                    )
                ON CONFLICT (plaid_transaction_id) DO NOTHING
            """), {
                "account_id": txn["account_id"],
                "plaid_id": txn["transaction_id"],
                "amount": txn["amount"],
                "merchant": txn.get("merchant_name"),
                "raw_name": txn["name"],
                "date": txn["date"],
                "pending": txn["pending"],
                "channel": txn.get("payment_channel")
            })

        # Step 4 - update cursor
        db.execute(text(
            "UPDATE institutions SET cursor = :cursor, last_synced_at = NOW() WHERE id = :id"
        ), {"cursor": response['next_cursor'], "id": str(institution.id)})

        db.commit()
        return {"synced": len(transactions)}

    finally:
        db.close()
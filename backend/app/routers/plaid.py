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
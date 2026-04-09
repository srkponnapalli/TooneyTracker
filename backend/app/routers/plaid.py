from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_transactions import LinkTokenTransactions
from fastapi import APIRouter
from app.services.plaid_service import client




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
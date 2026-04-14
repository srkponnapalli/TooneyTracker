import plaid
from dotenv import load_dotenv
from plaid.api import plaid_api
import os 

load_dotenv()
client_id = os.getenv("PLAID_CLIENT_ID")
secret = os.getenv("PLAID_SECRET")
environment = os.getenv("PLAID_ENV").capitalize()

# Available environments are
# 'Production'
# 'Sandbox'
configuration = plaid.Configuration(
    host=getattr(plaid.Environment, environment), #dynamic access to environment variable
    api_key={
        'clientId': client_id,
        'secret': secret,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
from fastapi import FastAPI

from app.db.connection import SessionLocal
from sqlalchemy import text
from app.routers.plaid import router as plaid_router
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
app.include_router(plaid_router, prefix="/plaid")



@app.get("/health")
def function_name():
    return {"Health": "is_good"}


@app.get("/db-health")
def db_health():
    try:
        db = SessionLocal()
        db.execute(text("Select 1"))
        return {"DB Health": "is_good"}
    except Exception as e:
        return {"DB Health": "is_bad", "error": str(e)}
    finally:
        db.close()



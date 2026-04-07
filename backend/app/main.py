from fastapi import FastAPI

from app.db.connection import SessionLocal
from sqlalchemy import text

app = FastAPI()


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
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def function_name():
    return {"Health": "is_good"}
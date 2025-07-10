from redis import Redis
import redis
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv("credentials.env")

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
PASS = os.getenv("PASS")
DATA = os.getenv("DATA")

app = FastAPI()

r = Redis(host=HOST, port=int(PORT), password=PASS, decode_responses=True)

@app.post("/create")
def create_key(key: str, value: str, expire: int):
    scoped_key = f"{DATA}:{key}"
    existing = r.get(scoped_key)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Key already exists.")
    r.setex(scoped_key, expire, value)
    return {"message": f"Key '{key}' created with value '{value}'"}

@app.get("/read")
def get_key(key: str):
    scoped_key = f"{DATA}:{key}"
    value = r.get(scoped_key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found.")
    return value

@app.get("/readkeys")  # Stretch
def show_keys():
    keys = []
    for pair in r.keys(f"{DATA}:*"):
        keys.append(pair.replace(f"{DATA}:", ""))
    return keys

@app.put("/update")
def update_key(key: str, value: str):
    try:
        scoped_key = f"{DATA}:{key}"
        if r.get(scoped_key) is not None:
            r.set(scoped_key, value)
            return {"message": f"Key '{key}' updated with value '{value}'"}
        raise HTTPException(status_code=404, detail="Key not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete")
def delete_key(key: str):
    try:
        scoped_key = f"{DATA}:{key}"
        if r.get(scoped_key) is None:
            raise HTTPException(status_code=404, detail="Key not found.")
        r.delete(scoped_key)
        return {"message": f"Key '{key}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

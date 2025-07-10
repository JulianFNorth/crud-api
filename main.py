from redis import Redis
import os
from dotenv import load_dotenv
load_dotenv("credentials.env")

HOST=os.getenv("HOST")
PORT=os.getenv("PORT")
PASS=os.getenv("PASS")
DATA=os.getenv("DATA")

app = FastAPI()

r = Redis(host=HOST, port=int(PORT), password=PASS, decode_responses=True)

@app.post("/create")
def create_key(key: str, value: str):
    if r.json().get(DATA, f".{key}") is not None:
        raise HTTPException(status_code=409, detail="Key already exists.")
    if r.exists(DATA) == 0:
        r.json().set(DATA, ".", {key: value})
    return {"message": f"Key '{key}' created with value '{value}'"}

@app.get("/read")
def get_key(key: str):
    value = r.json().get(DATA, f".{key}")
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found.")
    return value
@app.put("/update")
def update_key(key: str, value: str):
    try:
        data = r.json().set(DATA, f".{key}", value)
        if data is not None:
            return {"message": f"Key '{key}' updated with value '{value}'"}
        raise HTTPException(status_code=404, detail="Key not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete")
def delete_key(key: str):
    try:
        r.json().delete(DATA, f".{key}")
        return {"message": f"Key '{key}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
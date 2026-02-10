from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
from datetime import datetime
import os

app = FastAPI()

student_id = 0
Student = {}

class User(BaseModel):
    name: str
    age: int

LOG_FILE = "request_logs.json"


@app.middleware("http")
async def store_request_data(request: Request, call_next):
    data = {
        "time": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "headers": dict(request.headers),
        "cookies": request.cookies,
        "ip":request.client.host
    }

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    logs.append(data)

    
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    response = await call_next(request)
    return response


@app.get("/")
async def home():
    return {"message": "Hello"}


@app.post("/user")
async def add_user(user: User):
    global student_id

    item = {
        "name": user.name,
        "age": user.age
    }

    Student[student_id] = item
    student_id += 1

    with open("data.json", "w") as f:
        json.dump(Student, f, indent=2)

    return {
        "message": "SUCCESSFULLY ADDED",
        "data": item
    }


@app.get("/user")
async def show():
    
    if not os.path.exists("data.json"):
        return {"DATA": {}}

    with open("data.json", "r") as f:
        data = json.load(f)
        print(data)

    return {"DATA": data}


@app.get("/user/{userid}")
async def show_one(userid: int):
    
    if not os.path.exists("data.json"):
        raise HTTPException(status_code=404, detail="User not found")

    with open("data.json", "r") as f:
        p = json.load(f)

    userid = str(userid)

    if userid in p:
        return {"data": p[userid]}
    else:
        raise HTTPException(status_code=404, detail="User not found")
# test

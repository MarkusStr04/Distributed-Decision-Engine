from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserData(BaseModel):
    income: int
    age: int
    debt: int

@app.post("/decision")
def make_decision(data: UserData):
    score = data.income * 0.5 - data.debt * 0.3 + data.age * 2
    
    if score > 2000:
        return {"decision": "APPROVED", "score": score}
    else:
        return {"decision": "REJECTED", "score": score}
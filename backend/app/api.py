from fastapi import FastAPI
from engine import OpenF1Engine

app = FastAPI()
engine = OpenF1Engine()

@app.get("/status")
def status():
    return {"status": "running", "laps": engine.laps_completed()}

@app.post("/simulate")
def simulate(data: dict):
    result = engine.run(data)
    return result

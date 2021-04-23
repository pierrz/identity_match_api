from fastapi import FastAPI
from src.identity_match_score import IdentityMatchDataframe
from pathlib import Path
import os

app = FastAPI()
data_path = Path(os.getcwd(), "data", "examples_data.json")


@app.get("/")
async def root():
    processed_data = IdentityMatchDataframe()
    processed_data.import_and_process_data(data_path)
    results = processed_data.identity_match_scores
    return {"message": results}

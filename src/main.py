from fastapi import FastAPI, Request
from src.identity_match_score import IdentityMatchDataframe
from pathlib import Path
import os
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
data_path = Path(os.getcwd(), "data", "examples_data.json")
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


def prepare_results():
    processed_data = IdentityMatchDataframe()
    processed_data.import_and_process_data(data_path)
    return processed_data


@app.get("/service_api")
async def root():
    results = prepare_results()
    return {"identity_match_scores": results.identity_match_scores}


@app.get("/service_ui", response_class=HTMLResponse)
async def display_results(request: Request):

    data = prepare_results()
    data.clean_data["score"] = data.identity_match_scores
    for col in ["birthdate1", "birthdate2"]:
        data.clean_data[col] = data.clean_data[col].dt.strftime("%Y-%m-%d")
    output = data.clean_data.to_dict(orient="index")

    return templates.TemplateResponse(
        "display_results.html", {"request": request, "data": output}
    )

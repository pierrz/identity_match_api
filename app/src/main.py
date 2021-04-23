from src.identity_match_score import IdentityMatchDataframe
from pathlib import Path
import os
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import secrets
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI()
default_data_path = Path(os.getcwd(), "data", "examples.json")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBasic()


def check_api_key(api_key: str) -> str:
    list_api_keys = ["apikey123"]
    correct_api_key = secrets.compare_digest(api_key, "apikey123")
    if not (api_key in list_api_keys and correct_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect API key",
        )
    else:
        return True


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "service_ui_admin")
    correct_password = secrets.compare_digest(credentials.password, "ponytail")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def prepare_results(file_path: str = default_data_path):
    processed_data = IdentityMatchDataframe()
    processed_data.import_and_process_data(file_path)
    return processed_data


@app.get("/service_api/default")
async def export_default_results():
    results = prepare_results(default_data_path)
    return {"identity_match_scores": results.identity_match_scores}


@app.get("/service_api/")
async def export_results(filepath: str, apikey: str):
    if check_api_key(apikey):
        results = prepare_results(filepath)
        return {"identity_match_scores": results.identity_match_scores}


@app.get("/service_ui", response_class=HTMLResponse)
def display_results(request: Request, username: str = Depends(get_current_username)):

    data = prepare_results()
    data.clean_data["score"] = data.identity_match_scores
    for col in ["birthdate1", "birthdate2"]:
        data.clean_data[col] = data.clean_data[col].dt.strftime("%Y-%m-%d")
    output = data.clean_data.to_dict(orient="index")

    return templates.TemplateResponse(
        "display_results.html", {"request": request, "data": output}
    )

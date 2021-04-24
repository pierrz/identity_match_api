from src.identity_match_score import IdentityMatchDataframe
from pathlib import Path
import os
import pandas as pd
from typing import Optional
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import secrets
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel


app = FastAPI()
default_data_path = Path(os.sep, "data", "examples.json")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBasic()


class ScoresFrameAPI(BaseModel):

    source_path: Optional[str] = None
    data: pd.Series

    def prepare_results(self, file_path: str = default_data_path):
        processed_data = IdentityMatchDataframe()
        processed_data.import_and_process_data(file_path)
        self.data = processed_data.identity_match_scores


class ScoresFrameUI(ScoresFrameAPI):
    data_for_ui: dict
    def prepare_data_for_ui(self) -> dict:
        """Prepare an extended and refined version of the 'clean_data' frame"""
        self.data.clean_data["score"] = self.data.identity_match_scores
        for col in ["birthdate1", "birthdate2"]:
            self.data.clean_data[col] = self.data.clean_data[col].dt.strftime("%Y-%m-%d")
        self.data_for_ui = self.data.clean_data.to_dict(orient="index")


def check_api_key(api_key: str) -> str:
    correct_api_key = secrets.compare_digest(api_key, "apikey123")
    if not correct_api_key:
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


@app.get("/service_api_default")
async def export_default_results(apikey: str):
    if check_api_key(apikey):
        results = ScoresFrameAPI()
        results.prepare_results()
        return results


@app.get("/service_api")
async def export_results(filepath: str, apikey: str):
    if check_api_key(apikey):
        results = ScoresFrameAPI()
        results.prepare_results(filepath)
        return results


@app.get("/service_ui", response_class=HTMLResponse)
def display_results(request: Request, username: str = Depends(get_current_username)):

    results = ScoresFrameUI()
    results.prepare_results()
    results.prepare_data_for_ui()

    return templates.TemplateResponse(
        "display_results.html", {"request": request, "data": results.data_for_ui}
    )

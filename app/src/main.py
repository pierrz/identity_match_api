import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.models.models import ScoresFrameAPI, ScoresFrameUI
from src.config import Config as cfg

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBasic()


def check_api_key(api_key: str) -> str:
    correct_api_key = secrets.compare_digest(api_key, cfg.apikey_test)
    if not correct_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API key",
        )
    else:
        return True


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, cfg.ui_admin_id)
    correct_password = secrets.compare_digest(credentials.password, cfg.ui_admin_pwd)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def prepare_results_based_on_filepath(results, filepath: str):
    if filepath is None:
        results.prepare_results()
    else:
        results.prepare_results(filepath)


# API elements
def get_api_data(apikey: str, filepath: str = None):
    if check_api_key(apikey):
        results = ScoresFrameAPI()
        prepare_results_based_on_filepath(results, filepath)
        results.prepare_data_for_api()
        return results.api_data


@app.get("/service_api_default")
async def export_default_results(apikey: str):
    return get_api_data(apikey)


@app.get("/service_api")
async def export_results(filepath: str, apikey: str):
    return get_api_data(apikey, filepath)


# UI elements
def get_ui_data(filepath: str = None):
    results = ScoresFrameUI()
    prepare_results_based_on_filepath(results, filepath)
    results.prepare_data_for_ui()
    return results.ui_data


@app.get("/service_ui_default", response_class=HTMLResponse)
def display_default_results(
    request: Request, username: str = Depends(get_current_username)
):
    return templates.TemplateResponse(
        "display_results.html", {"request": request, "data": get_ui_data()}
    )


@app.get("/service_ui", response_class=HTMLResponse)
def display_results(
    filepath: str,
    apikey: str,
    request: Request,
    username: str = Depends(get_current_username),
):
    return templates.TemplateResponse(
        "display_results.html", {"request": request, "data": get_ui_data(filepath)}
    )

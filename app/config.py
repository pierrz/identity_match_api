import os
from pathlib import Path


class Config:
    default_data_path = Path(Path(os.getcwd()).parent, "data", "examples.json")
    apikey_test = "apikey123"
    ui_admin_id = "service_ui_admin"
    ui_admin_pwd = "ponytail"

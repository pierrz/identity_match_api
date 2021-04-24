import os
from pathlib import Path


class Config:
    default_data_path = Path(Path(os.getcwd()).parent, "data", "examples.json")

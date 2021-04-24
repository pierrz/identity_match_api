from typing import Optional

import pandas as pd
from config import Config as cfg
from pydantic import BaseModel
from src.identity_match_score import IdentityMatchDataframe


class ScoresFrameBase(BaseModel):
    source_path: Optional[str] = None
    results: Optional[pd.DataFrame]

    class Config:
        arbitrary_types_allowed = True

    def prepare_results(self, file_path: str = cfg.default_data_path):
        processed_data = IdentityMatchDataframe()
        processed_data.import_and_process_data(file_path)
        self.results = processed_data


class ScoresFrameAPI(ScoresFrameBase):

    api_data: Optional[pd.Series]

    def prepare_data_for_api(self):
        self.api_data = self.results.identity_match_scores


class ScoresFrameUI(ScoresFrameBase):
    ui_data: Optional[dict]

    def prepare_data_for_ui(self) -> dict:
        """Prepare an extended and refined version of the 'clean_data' frame"""
        self.results.clean_data["score"] = self.results.identity_match_scores
        for col in ["birthdate1", "birthdate2"]:
            self.results.clean_data[col] = self.results.clean_data[col].dt.strftime(
                "%Y-%m-%d"
            )
        self.ui_data = self.results.clean_data.to_dict(orient="index")

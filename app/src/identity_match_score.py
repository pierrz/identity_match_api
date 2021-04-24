import json
from typing import List, Tuple, Union

import pandas as pd

from utils.src_utils import (compare_values, get_score,
                             get_string_distance_scores,
                             remove_string_with_regex)


class IdentityMatchDataframe:

    raw_data: pd.DataFrame
    clean_data: pd.DataFrame
    identity_match_scores: pd.Series
    input_col_names: List[str] = ["fullname", "birthdate", "bsn"]
    firstname_cols_meta: Tuple[List[str], str] = (
        ["firstname1", "firstname2"],
        "identical_first_name",
    )
    lastname_cols_meta: Tuple[List[str], str] = (
        ["lastname1", "lastname2"],
        "identical_last_name",
    )
    birthdate_cols_meta: Tuple[List[str], str] = (
        ["birthdate1", "birthdate2"],
        "identical_birthdate",
    )
    bsn_cols_meta: Tuple[List[str], str] = (["bsn1", "bsn2"], "identical_bsn")

    def import_and_process_data(self, file_path: str):
        data = json.load(open(file_path, "r"))
        self.raw_data = pd.DataFrame.from_dict(data, orient="index")
        self.clean_data = self.prepare_clean_data()
        self.identity_match_scores = self.calculate()

    def prepare_clean_data(self) -> pd.DataFrame:
        df_list = list()

        for col in ["id1", "id2"]:
            current_col_names = [f"{name}{col[-1]}" for name in self.input_col_names]
            dtypes = dict(zip(current_col_names, [str, "datetime64[ns]", "Int64"]))
            mapping = dict(zip(self.input_col_names, current_col_names))
            expanded_dicts_df = (
                pd.DataFrame(self.raw_data[col].tolist(), index=self.raw_data.index,)
                .rename(columns=mapping)
                .astype(dtypes)
            )
            expanded_dicts_df[f"firstname{col[-1]}"] = self.get_first_name_string(
                expanded_dicts_df[f"fullname{col[-1]}"]
            )
            expanded_dicts_df[f"lastname{col[-1]}"] = self.get_last_name_string(
                expanded_dicts_df[f"fullname{col[-1]}"]
            )
            expanded_dicts_df.drop(columns=[f"fullname{col[-1]}"], inplace=True)
            df_list.append(expanded_dicts_df)

        return df_list[0].join(df_list[1:])

    def calculate(self) -> pd.Series:
        """
        - If the dates of birth are known and not the same, there is no match
        - If the BSN number matches then 100%
        - Otherwise:
            o If the last name is the same: +40%
            o If the first name is the same: +20%
            o If the first name is similar: +15%
            o If the date of birth matches: + 40%
        """

        identical_bsn_mask = compare_values(self.bsn_cols_meta[0], self.clean_data)
        not_identical_birthdate_mask = compare_values(
            self.birthdate_cols_meta[0], self.clean_data, "not"
        )
        self.clean_data[self.bsn_cols_meta[1]] = identical_bsn_mask
        no_match_values = pd.Series(0.0, index=self.clean_data.index)
        match_values = pd.Series(1.0, index=self.clean_data.index)

        no_bsn_date_match_values = (
            self.get_last_name_score()
            + self.get_first_name_score()
            + self.get_birthdate_score()
        )

        # needs roundind to avoid results with long trail such as 0.6000000000000001
        return no_match_values.where(
            not_identical_birthdate_mask,
            other=match_values.where(
                identical_bsn_mask, other=no_bsn_date_match_values
            ),
        ).round(2)

    @staticmethod
    def get_last_name_string(values: pd.Series) -> pd.Series:
        return remove_string_with_regex(values, ".* ")

    @staticmethod
    def get_first_name_string(values: Union[pd.Series, str]) -> Union[pd.Series, str]:
        if type(values) == str:
            values = pd.Series(values)
        return remove_string_with_regex(values, " .*")

    def get_birthdate_score(self) -> pd.Series:
        return get_score(
            self.birthdate_cols_meta[0],
            self.clean_data,
            self.birthdate_cols_meta[1],
            0.4,
        )

    def get_last_name_score(self) -> pd.Series:
        return get_score(
            self.lastname_cols_meta[0], self.clean_data, self.lastname_cols_meta[1], 0.4
        )

    def get_first_name_score(self) -> pd.Series:
        scores = get_score(
            self.firstname_cols_meta[0],
            self.clean_data,
            self.firstname_cols_meta[1],
            0.2,
        )
        return scores.where(
            scores > 0, other=self.get_firstname_string_distance_score()
        )

    def get_firstname_string_distance_score(self) -> pd.Series:

        distance_scores = pd.Series(
            get_string_distance_scores(self.firstname_cols_meta[0], self.clean_data),
            index=self.clean_data.index,
        )
        self.clean_data["first_name_string_distance"] = distance_scores > 0.0
        return distance_scores

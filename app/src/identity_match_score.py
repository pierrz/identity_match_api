from typing import Union
import pandas as pd
import json
from nltk.metrics.distance import edit_distance

"""
TODO:
- doc
- docker
"""


class IdentityMatchDataframe:

    raw_data: pd.DataFrame
    clean_data: pd.DataFrame
    identity_match_scores: pd.Series
    input_col_names = ["fullname", "birthdate", "bsn"]
    firstname_cols = ["firstname1", "firstname2"]
    lastname_cols = ["lastname1", "lastname2"]

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
                pd.DataFrame(
                    self.raw_data[col].tolist(),
                    index=self.raw_data.index,
                )
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

        identical_bsn_mask = self.compare_values("bsn1", "bsn2")
        not_identical_birthdate_mask = self.compare_values(
            "birthdate1", "birthdate2", "not"
        )
        self.clean_data["identical_bsn"] = identical_bsn_mask
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

    def get_notna_mask(self, col1_name: str, col2_name: str) -> pd.Series:
        return self.clean_data[col1_name].notna() & self.clean_data[col2_name].notna()

    def compare_values(self, col1_name: str, col2_name: str, *args) -> pd.Series:
        not_na_mask = self.get_notna_mask(col1_name, col2_name)
        identical_values_mask = self.clean_data[col1_name] == self.clean_data[col2_name]
        if len(args) == 1:
            return ~identical_values_mask & not_na_mask
        return identical_values_mask & not_na_mask

    def get_birthdate_score(self) -> pd.Series:
        identical_birthdates_mask = self.compare_values("birthdate1", "birthdate2")
        self.clean_data["identical_birthdate"] = identical_birthdates_mask
        return pd.Series(0.4, index=self.clean_data.index).where(
            identical_birthdates_mask, other=0.0
        )

    @staticmethod
    def get_last_name_string(values: pd.Series) -> pd.Series:
        return values.str.replace(".* ", "", regex=True)

    @staticmethod
    def get_first_name_string(values: Union[pd.Series, str]) -> Union[pd.Series, str]:
        if type(values) == str:
            values = pd.Series(values)
        return values.str.replace(" .*", "", regex=True)

    def get_last_name_score(self) -> pd.Series:
        identical_last_name_mask = self.compare_values(*self.lastname_cols)
        self.clean_data["identical_last_name"] = identical_last_name_mask
        return pd.Series(0.4, index=self.clean_data.index).where(
            identical_last_name_mask, other=0.0
        )

    def get_first_name_score(self) -> pd.Series:
        identical_first_name_mask = self.compare_values(*self.firstname_cols)
        self.clean_data["identical_first_name"] = identical_first_name_mask
        return pd.Series(0.2, index=self.clean_data.index).where(
            identical_first_name_mask, other=self.get_firstname_string_distance_score()
        )

    def get_firstname_string_distance_score(self) -> pd.Series:
        col1_name, col2_name = self.firstname_cols

        score_values = list()
        for idx, r in self.clean_data[self.firstname_cols].iterrows():

            # Calculate the Levenshtein edit-distance between two strings
            string_distance = edit_distance(
                r[col1_name],
                r[col2_name],
                substitution_cost=1,
                transpositions=False,
            )

            # check if 2nd string is either initials or similar enough for typo/diminutive
            if (
                r[col2_name] == f"{r[col1_name][0]}."
                or string_distance <= len(r[col1_name]) / 2
            ):
                r_score = 0.15
            else:
                r_score = 0.0
            score_values.append(r_score)

        firstname_string_distance_scores = pd.Series(
            score_values, index=self.clean_data.index
        )
        self.clean_data["first_name_string_distance"] = (
            firstname_string_distance_scores > 0.0
        )
        return firstname_string_distance_scores

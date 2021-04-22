from typing import Union
import pandas as pd
from nltk.metrics.distance import edit_distance

data = {
    "pair1": {
        "id1": {"fullname": "Andrew Craw", "birthdate": "20-02-1985", "bsn": None},
        "id2": {"fullname": "Andrew Craw", "birthdate": None, "bsn": None},
        "identity_match_score": 0.6,
    },
    "pair2": {
        "id1": {"fullname": "Andrew Craw", "birthdate": "20-02-1985", "bsn": None},
        "id2": {"fullname": "Petty Smith", "birthdate": "20-02-1985", "bsn": None},
        "identity_match_score": 0.4,
    },
    "pair3": {
        "id1": {"fullname": "Andrew Craw", "birthdate": "20-02-1985", "bsn": None},
        "id2": {"fullname": "A. Craw", "birthdate": "20-02-1985", "bsn": None},
        "identity_match_score": 0.95,
    },
    "pair4": {
        "id1": {"fullname": "Andrew Craw", "birthdate": "20-02-1985", "bsn": 931212312},
        "id2": {"fullname": "Petty Smith", "birthdate": "20-02-1985", "bsn": 931212312},
        "identity_match_score": 1,
    },
}

"""
TODO:
- unit test
- auth
- doc
- docker & tox
- SAP
"""


class IdentityMatchDataframe:
    raw_data = pd.DataFrame.from_dict(data, orient="index")
    col_names = ["fullname", "birthdate", "bsn"]
    fullname_cols = ["fullname1", "fullname2"]

    def __init__(self):
        self.clean_data = self.prepare_clean_data()
        self.similarity_score = self.calculate()

    def prepare_clean_data(self):
        df_list = list()

        for col in ["id1", "id2"]:
            current_col_names = [f"{name}{col[-1]}" for name in self.col_names]
            dtypes = dict(zip(current_col_names, [str, "datetime64[ns]", "Int64"]))
            mapping = dict(zip(self.col_names, current_col_names))
            expanded_dicts_df = (
                pd.DataFrame(
                    self.raw_data[col].tolist(),
                    index=self.raw_data.index,
                )
                .rename(columns=mapping)
                .astype(dtypes)
            )
            df_list.append(expanded_dicts_df)

        return self.raw_data["identity_match_score"].to_frame().join(df_list)

    def calculate(self):
        """
        - If the dates of birth are known and not the same, there is no match
        - If the BSN number matches then 100%
        - Otherwise:
            o If the last name is the same: +40%
            o If the first name is the same: +20%
            o If the first name is similar: +15%
            o If the date of birth matches: + 40%
        """

        identical_bsn_mask = self.compare_dates_or_integers("bsn1", "bsn2")
        not_identical_birthdate_mask = self.compare_dates_or_integers(
            "birthdate1", "birthdate2", "not"
        )
        no_match_values = pd.Series(0.0, index=self.clean_data.index)
        match_values = pd.Series(1.0, index=self.clean_data.index)

        no_bsn_date_match_values = (
            self.get_last_name_score()
            + self.get_first_name_score()
            + self.get_birthdate_score()
        )

        return no_match_values.where(
            not_identical_birthdate_mask,
            other=match_values.where(
                identical_bsn_mask, other=no_bsn_date_match_values
            ),
        )

    def get_notna_mask(self, col1_name: str, col2_name: str):
        return self.clean_data[col1_name].notna() & self.clean_data[col2_name].notna()

    def compare_dates_or_integers(self, col1_name: str, col2_name: str, *args):
        not_na_mask = self.get_notna_mask(col1_name, col2_name)
        identical_values_mask = self.clean_data[col1_name] == self.clean_data[col2_name]
        if len(args) == 1:
            return ~identical_values_mask & not_na_mask
        return identical_values_mask & not_na_mask

    def get_bsn_score(self):
        identical_bsn_mask = self.compare_dates_or_integers("bsn1", "bsn2")
        return pd.Series(1.0, index=self.clean_data.index).where(
            identical_bsn_mask, other=0.0
        )

    def get_birthdate_score(self):
        identical_dates_mask = self.compare_dates_or_integers(
            "birthdate1", "birthdate2"
        )
        return pd.Series(0.4, index=self.clean_data.index).where(
            identical_dates_mask, other=0.0
        )

    @staticmethod
    def get_last_name_string(values: pd.Series) -> pd.Series:
        return values.str.replace(".* ", " ", regex=True)

    @staticmethod
    def get_first_name_string(values: Union[pd.Series, str]) -> Union[pd.Series, str]:
        if type(values) == str:
            values = pd.Series(values)
        return values.str.replace(" .*", " ", regex=True)

    def get_last_name_score(self):
        col1_name, col2_name = self.fullname_cols
        not_na_mask = self.get_notna_mask(col1_name, col2_name)

        last_name_mask = self.get_last_name_string(
            self.clean_data[col1_name]
        ) == self.get_last_name_string((self.clean_data[col2_name]))

        return pd.Series(0.4, index=self.clean_data.index).where(
            (last_name_mask & not_na_mask), other=0.0
        )

    def get_first_name_score(self):
        col1_name, col2_name = self.fullname_cols
        not_na_mask = self.get_notna_mask(col1_name, col2_name)

        first_name_mask = self.get_first_name_string(
            self.clean_data[col1_name]
        ) == self.get_first_name_string((self.clean_data[col2_name]))

        return pd.Series(0.2, index=self.clean_data.index).where(
            (first_name_mask & not_na_mask), other=self.get_fullname_similarity_score()
        )

    def get_fullname_similarity_score(self):
        col1_name, col2_name = self.fullname_cols
        default_score = 0.15

        score_values = list()
        for idx, r in self.clean_data[self.fullname_cols].iterrows():

            # Calculate the Levenshtein edit-distance between two strings
            string_distance = edit_distance(
                r[col1_name],
                r[col2_name],
                substitution_cost=1,
                transpositions=False,
            )

            # check if 2nd string is either initials or similar enough for typo/diminutive
            if (
                r[col2_name] == f"{self.get_first_name_string(r[col2_name])[0]}."
                or string_distance <= 6
            ):
                r_score = default_score
            else:
                r_score = 0.0
            score_values.append(r_score)

        return pd.Series(score_values, index=self.clean_data.index)


if __name__ == "__main__":
    df = IdentityMatchDataframe()
    # print(df.clean_data)
    print(df.similarity_score)

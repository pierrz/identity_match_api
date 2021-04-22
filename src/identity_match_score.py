import pandas as pd
from typing import List

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


class IdentityMatchDataframe:
    raw_data = pd.DataFrame.from_dict(data, orient="index")
    col_names = ["fullname", "birthdate", "bsn"]

    def __init__(self):
        self.clean_data = self.prepare_clean_data()

    def prepare_clean_data(self):
        df_list = list()

        for col in ["id1", "id2"]:
            current_col_names = [f"{name}{col[-1]}" for name in self.col_names]
            dtypes = dict(zip(current_col_names, [str, "datetime64[ns]", "Int64"]))
            mapping = dict(zip(self.col_names, current_col_names))
            expanded_dicts_df = (
                pd.DataFrame(self.raw_data[col].tolist(), index=self.raw_data.index,)
                .rename(columns=mapping)
                .astype(dtypes)
            )
            df_list.append(expanded_dicts_df)

        return self.raw_data["identity_match_score"].to_frame().join(df_list)

    def calculate(self):
        bsn_mask = self.clean_data["bsn1"] == self.clean_data["bsn2"]
        different_bsn_scores = 0.0
        results = pd.Series(1.0, index=self.clean_data.index).where(
            bsn_mask, other=different_bsn_scores
        )

    # def get_bsn_score(self):
    #     comparison_mask = self.clean_data["bsn1"] == self.clean_data["bsn2"]
    #     return pd.Series(1.0, index=self.clean_data.index).where(comparison_mask, other=0.0)

    @staticmethod
    def get_last_name_string(values: pd.Series) -> pd.Series:
        return values.str.replace(".* ", " ", regex=True)

    @staticmethod
    def get_first_name_string(values: pd.Series) -> pd.Series:
        return values.str.replace(" .*", " ", regex=True)

    def get_last_name_score(self):
        comparison_mask = self.get_last_name_string(
            self.clean_data["fullname1"]
        ) == self.get_last_name_string((self.clean_data["fullname2"]))
        return pd.Series(0.4, index=self.clean_data.index).where(
            comparison_mask, other=0.0
        )

    def get_first_name_score(self):
        comparison_mask = self.get_first_name_string(
            self.clean_data["fullname1"]
        ) == self.get_first_name_string((self.clean_data["fullname2"]))
        return pd.Series(0.2, index=self.clean_data.index).where(
            comparison_mask, other=0.0
        )

    def get_birthdate_score(self):
        not_na_mask = (
            self.clean_data["birthdate1"].notna()
            & self.clean_data["birthdate2"].notna()
        )
        identical_dates_mask = (
            self.clean_data["birthdate1"] == self.clean_data["birthdate2"]
        ) & not_na_mask
        # not_identical_dates_mask = self.clean_data["birthdate1"] == self.clean_data["birthdate2"] & not_na_mask
        return pd.Series(0.4, index=self.clean_data.index).where(
            identical_dates_mask, other=0.0
        )


if __name__ == "__main__":
    df = IdentityMatchDataframe()
    # print(df.raw_data)
    # print(df.clean_data)
    print(df.get_last_name_score())

    """
    - If the BSN number matches then 100%
    - Otherwise:
    o Ifthelastnameisthesame+40%
    o Ifthefirstnameisthesame+20%
    o Ifthefirstnameissimilar+15%(seeexamples)
    o If the date of birth matches + 40%
    o If the dates of birth are known and not the same, there is no match
    """

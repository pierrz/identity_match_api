import pandas as pd
from nltk.corpus.reader.wordnet import lin_similarity

# from nltk.corpus import wordnet as wn
import nltk

nltk.download("wordnet")
wn = nltk.corpus.wordnet

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
    fullname_cols = ["fullname1", "fullname2"]

    def __init__(self):
        self.clean_data = self.prepare_clean_data()
        self.get_fullname_similarity_score()

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
        bsn_mask = self.clean_data["bsn1"] == self.clean_data["bsn2"]
        different_bsn_scores = 0.0
        results = pd.Series(1.0, index=self.clean_data.index).where(
            bsn_mask, other=different_bsn_scores
        )

    def get_notna_mask(self, col1_name: str, col2_name: str):
        return self.clean_data[col1_name].notna() & self.clean_data[col2_name].notna()

    def compare_dates_or_integers(self, col1_name: str, col2_name: str):
        not_na_mask = self.get_notna_mask(col1_name, col2_name)
        identical_values_mask = (
            self.clean_data[col1_name] == self.clean_data[col2_name]
        ) & not_na_mask
        return identical_values_mask

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
    def get_first_name_string(values: pd.Series) -> pd.Series:
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
            (first_name_mask & not_na_mask), other=0.0
        )

    def get_fullname_similarity_score(self):
        col1_name, col2_name = self.fullname_cols

        score_values = list()
        for idx, r in self.clean_data[self.fullname_cols].iterrows():
            # print(lin_similarity(r[col1_name], r[col2_name], ic="semcor_ic"))
            score_values.append(
                lin_similarity(
                    wn.synset(f"{r[col1_name]}.n.01"),
                    wn.synset(f"{r[col2_name]}.n.01"),
                    ic="semcor_ic",
                )
            )

        self.clean_data["similarity_score"] = score_values

        # wn.synset(f"{r[col1_name]}.n.01")
        # df = self.clean_data[self.fullname_cols].apply(lambda x: lin_similarity(
        #     synset1=x[col1_name],
        #     synset2=x[col2_name],
        #     ic="semcor_ic"
        # ))
        # return df


if __name__ == "__main__":
    df = IdentityMatchDataframe()
    # print(df.raw_data)
    print(df.clean_data)
    print(df.clean_data["similarity_score"])
    # print(df.get_fullname_similarity_score())

    """
    - If the BSN number matches then 100%
    - Otherwise:
        o Ifthelastnameisthesame+40%
        o Ifthefirstnameisthesame+20%
    o Ifthefirstnameissimilar+15%(seeexamples)
        o If the date of birth matches + 40%
    o If the dates of birth are known and not the same, there is no match
    """

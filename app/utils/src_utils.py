from typing import List

import pandas as pd
from nltk.metrics.distance import edit_distance


def remove_string_with_regex(values: pd.Series, regex_exp: str):
    return values.str.replace(regex_exp, "", regex=True)


def get_notna_mask(col_list: List, df: pd.DataFrame) -> pd.Series:
    col1_name, col2_name = col_list
    return df[col1_name].notna() & df[col2_name].notna()


def compare_values(col_list: List, df: pd.DataFrame, *args) -> pd.Series:
    col1_name, col2_name = col_list
    not_na_mask = get_notna_mask(col_list, df)
    identical_values_mask = df[col1_name] == df[col2_name]
    if len(args) == 1:
        return ~identical_values_mask & not_na_mask
    return identical_values_mask & not_na_mask


def get_score(
    col_list: List, df: pd.DataFrame, clean_col_flag_name: str, default_value: float
) -> pd.Series:
    identical_values_mask = compare_values(col_list, df)
    df[clean_col_flag_name] = identical_values_mask
    return pd.Series(default_value, index=df.index).where(
        identical_values_mask, other=0.0
    )


def get_string_distance_scores(col_list: List, df: pd.DataFrame) -> list:
    """ This could be improved with an approach using pandas vectorisation """
    col1_name, col2_name = col_list
    score_values = list()
    for idx, r in df[col_list].iterrows():

        # Calculate the Levenshtein edit-distance between two strings
        string_distance = edit_distance(
            r[col1_name], r[col2_name], substitution_cost=1, transpositions=False,
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
    return score_values

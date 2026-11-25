"""
Checkers for STEP 2 (practice/my_election_map/metrics.py).

These feed the FINISHED tool's long table into your functions, so Step 2
works even if your Step 1 isn't perfect yet.

Run:  python -m pytest practice -rs -k 2a      (or 2b, 2c, 2d)
"""
import math

import pandas as pd
import pytest

from my_election_map import metrics as mine

KEYS = ["contest", "ward", "subdiv"]


# ---------------------------------------------------------------- 2a
def test_2a_subdivision_totals(answer_long):
    totals = mine.subdivision_totals(answer_long)
    assert isinstance(totals, pd.Series), "return a Series (one number per subdivision)"
    assert totals.name == "total"
    assert list(totals.index.names) == KEYS
    assert len(totals) == 1_431
    assert totals.sum() == 982_660
    assert totals.loc[("Mayor", 1, 1)] == 466        # matches 'City Ward 1 Totals' on the sheet


# ---------------------------------------------------------------- 2b
def test_2b_winner_and_percentages(answer_long, answer_summary, same_rows):
    s = mine.summarize(answer_long)
    same_rows(s, answer_summary, KEYS + ["total", "winner_pct", "margin_pct"], KEYS)

    # Compare winners where there's a clear winner (ties are Step 2c).
    a = answer_summary.set_index(KEYS)
    m = s.set_index(KEYS).reindex(a.index)
    clear = a["winner"].ne("Tie")
    wrong = (m["winner"] != a["winner"])[clear]
    assert not wrong.any(), f"wrong winner in {wrong.sum()} subdivisions, e.g. {wrong[wrong].index[0]}"

    # Runner-up: only check subdivisions with one clear 2nd place.
    ranked = answer_long.sort_values("votes", ascending=False).groupby(KEYS)["votes"]
    second = ranked.nth(1).groupby([answer_long[k] for k in KEYS]).first()
    third = ranked.nth(2).groupby([answer_long[k] for k in KEYS]).first().reindex(second.index)
    clear2 = (second != third).reindex(a.index, fill_value=False) & clear
    wrong = (m["runner_up"] != a["runner_up"])[clear2]
    assert not wrong.any(), f"wrong runner_up in {wrong.sum()} subdivisions, e.g. {wrong[wrong].index[0]}"


# ---------------------------------------------------------------- 2c
def tiny_table():
    rows = [
        # subdivision 1: A and B tie
        (1, "A", 10), (1, "B", 10), (1, "C", 1),
        # subdivision 2: nobody voted
        (2, "A", 0), (2, "B", 0), (2, "C", 0),
        # subdivision 3: A wins clearly
        (3, "A", 5), (3, "B", 3), (3, "C", 0),
    ]
    return pd.DataFrame([{"contest": "Mayor", "ward": 1, "subdiv": s, "candidate": c, "votes": v}
                         for s, c, v in rows])


def test_2c_tie_is_called_a_tie():
    s = mine.summarize(tiny_table()).set_index("subdiv")
    assert s.loc[1, "winner"] == "Tie"
    assert s.loc[1, "margin_pct"] == 0
    assert s.loc[1, "winner_pct"] == 47.6          # 10 of 21
    assert s.loc[3, "winner"] == "A"
    assert s.loc[3, "margin_pct"] == 25.0          # (5 - 3) / 8


def test_2c_empty_poll_has_no_winner():
    s = mine.summarize(tiny_table()).set_index("subdiv")
    assert s.loc[2, "total"] == 0
    assert s.loc[2, "winner"] is None or pd.isna(s.loc[2, "winner"])
    assert math.isnan(s.loc[2, "winner_pct"]) and math.isnan(s.loc[2, "margin_pct"])


def test_2c_real_mayor_counts(answer_long):
    wins = mine.summarize(answer_long)["winner"].value_counts()
    assert wins["Chow Olivia"] == 1_014
    assert wins["Bradford Brad"] == 406
    assert wins["Tie"] == 11


# ---------------------------------------------------------------- 2d
def test_2d_head_to_head(answer_long, answer_summary, same_rows):
    s = mine.summarize(answer_long, compare=("Chow Olivia", "Bradford Brad"))
    same_rows(s, answer_summary, KEYS + ["a_pct", "b_pct", "a_minus_b"], KEYS)


def test_2d_no_compare_no_extra_columns(answer_long):
    s = mine.summarize(answer_long)
    assert "a_minus_b" not in s.columns

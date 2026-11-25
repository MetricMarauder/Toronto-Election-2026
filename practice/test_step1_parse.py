"""
Checkers for STEP 1 (practice/my_election_map/parse.py).

Run just one sub-step:  python -m pytest practice -rs -k 1a
Run all of step 1:      python -m pytest practice/test_step1_parse.py -rs

Try to write the code BEFORE reading these. They show exactly what's expected.
"""
import pandas as pd
import pytest

from conftest import DATA, MAYOR
from election_map import parse as answer
from my_election_map import parse as mine


# ---------------------------------------------------------------- 1a
@pytest.mark.parametrize("value,expected", [
    (3, True),
    (466.0, True),
    (0, True),
    (float("nan"), False),
    ("Total", False),
    ("99", False),          # text that LOOKS like a number is still text
    (None, False),
])
def test_1a_is_number(value, expected):
    assert mine.is_number(value) == expected


# ---------------------------------------------------------------- 1b
def test_1b_real_header_row(mayor_sheets):
    raw = mayor_sheets["Ward 1"]
    cells = raw.iloc[1, 1:]                 # the "Subdivision" row, minus its label
    cols = mine.subdivision_columns(cells)
    assert isinstance(cols, dict)
    assert cols[1] == 1 and cols[2] == 3 and cols[3] == 5
    assert cols[46] == 99
    assert 47 not in cols, "column 47 says 'Total'; it isn't a subdivision"
    assert len(cols) == 46
    assert all(isinstance(v, int) for v in cols.values()), "use int, not float (5, not 5.0)"


def test_1b_text_and_blanks():
    cells = pd.Series(["1", 2.0, "Total", float("nan"), " 99 "], index=[1, 2, 3, 4, 5])
    assert mine.subdivision_columns(cells) == {1: 1, 2: 2, 5: 99}


# ---------------------------------------------------------------- 1c
@pytest.mark.parametrize("label,expected", [
    ("City Ward 1 Totals", 1),
    ("City Ward 25 Totals", 25),
    ("City Ward 1 Etobicoke North", None),
    ("Chow Olivia", None),
    ("Subdivision", None),
])
def test_1c_ward_from_totals(label, expected):
    assert mine.ward_from_totals(label) == expected


# ---------------------------------------------------------------- 1d
COLUMNS = ["contest", "ward", "subdiv", "candidate", "votes"]
SORT = ["contest", "ward", "subdiv", "candidate"]


def test_1d_one_mayor_sheet(mayor_sheets, same_rows):
    raw = mayor_sheets["Ward 1"]
    same_rows(mine.parse_sheet(raw, "Ward 1", check_totals=False),
              answer.parse_sheet(raw, "Ward 1"), COLUMNS, SORT)


def test_1d_school_board_sheet_has_two_blocks(same_rows):
    # One school ward overlaps two city wards, so this sheet has TWO blocks.
    raw = pd.read_excel(DATA / "Poll_By_Poll_TDSB.xlsx", sheet_name="Ward 1", header=None)
    mine_rows = mine.parse_sheet(raw, "Ward 1", check_totals=False)
    same_rows(mine_rows, answer.parse_sheet(raw, "Ward 1"), COLUMNS, SORT)
    assert sorted(mine_rows["ward"].unique()) == [1, 7]


def test_1d_all_offices_sheet_has_six_races(same_rows):
    raw = pd.read_excel(DATA / "Poll_By_Poll_All_Offices.xlsx", sheet_name=0, header=None)
    same_rows(mine.parse_sheet(raw, "first", check_totals=False),
              answer.parse_sheet(raw, "first"), COLUMNS, SORT)


# ---------------------------------------------------------------- 1e
def test_1e_good_sheet_passes_the_check(mayor_sheets):
    mine.parse_sheet(mayor_sheets["Ward 1"], "Ward 1", check_totals=True)   # must not raise


def test_1e_a_wrong_number_is_caught(mayor_sheets):
    raw = mayor_sheets["Ward 1"].copy()
    raw.iat[5, 3] = 999                       # break one number on purpose
    with pytest.raises(mine.ParseError):
        mine.parse_sheet(raw, "Ward 1", check_totals=True)
    # ...and with the check switched off, it quietly reads the bad number.
    rows = mine.parse_sheet(raw, "Ward 1", check_totals=False)
    assert 999 in rows["votes"].tolist()


# ---------------------------------------------------------------- 1f
def test_1f_whole_workbook(answer_long, same_rows):
    long = mine.read_poll_by_poll(MAYOR)
    assert list(long.columns) == ["source", "sheet", "contest", "ward", "subdiv", "candidate", "votes"]
    assert long["votes"].sum() == 982_660, "the official citywide total"
    assert long["ward"].nunique() == 25
    assert (long["source"] == "Poll_By_Poll_Mayor.xlsx").all()
    same_rows(long, answer_long, list(long.columns), ["sheet", "ward", "subdiv", "candidate"])

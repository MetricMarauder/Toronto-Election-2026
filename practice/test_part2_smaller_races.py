"""
Checkers for PART 2: the smaller races (steps 6, 7, 8).

Run:  python -m pytest practice -rs -k 6a      (or 6b, 7a, 7b, 8a, 8b)
"""
import pandas as pd
import pytest

from conftest import DATA, answer
from my_election_map import parse as mine
from my_election_map import metrics as mine_metrics
from my_election_map.cli import main

COUNCILLOR = DATA / "Poll_By_Poll_Councillor.xlsx"
TDSB = DATA / "Poll_By_Poll_TDSB.xlsx"
FRENCH = DATA / "Poll_By_Poll_TFDSB.xlsx"            # Conseil scolaire Viamonde
ALL = DATA / "Poll_By_Poll_All_Offices.xlsx"
COLUMNS = ["source", "sheet", "contest", "ward", "subdiv", "candidate", "votes"]
SORT = ["sheet", "contest", "ward", "subdiv", "candidate"]


# ---------------------------------------------------------------- 6: Councillor
def test_6a_councillor_file_parses(same_rows):
    long = mine.read_poll_by_poll(COUNCILLOR)
    assert long["votes"].sum() == 932_157
    same_rows(long, answer("councillor_long"), COLUMNS, SORT)


def test_6b_one_ward_only(tmp_path):
    out = tmp_path / "ward10"
    assert main([str(COUNCILLOR), "--ward", "10", "--csv-only", "--out", str(out)]) == 0
    table = pd.read_csv(out.with_suffix(".csv"))
    assert set(table["ward"]) == {10}, "--ward 10 should keep only ward 10"
    assert len(table) == 80, "ward 10 has 80 subdivisions (including advance polls)"


def test_6b_margin_map(fake_shapes, tmp_path):
    shapes = tmp_path / "subdivisions.gpkg"
    fake_shapes.to_file(shapes)
    out = tmp_path / "councillor"
    assert main([str(COUNCILLOR), "--boundaries", str(shapes), "--color", "margin_pct",
                 "--out", str(out)]) == 0
    assert out.with_suffix(".html").exists()


# ---------------------------------------------------------------- 7: School boards
def test_7a_sheet_with_two_blocks(same_rows):
    # School ward 1 overlaps city wards 1 and 7, so this sheet has TWO blocks.
    raw = pd.read_excel(TDSB, sheet_name="Ward 1", header=None)
    rows = mine.parse_sheet(raw, "Ward 1")
    cols = ["contest", "ward", "subdiv", "candidate", "votes"]
    tdsb = answer("tdsb_long")
    same_rows(rows, tdsb[tdsb.sheet == "Ward 1"], cols, cols[:4])
    assert sorted(rows["ward"].unique()) == [1, 7]


def test_7a_whole_school_board_file(same_rows):
    long = mine.read_poll_by_poll(TDSB)
    assert long["votes"].sum() == 672_546
    same_rows(long, answer("tdsb_long"), COLUMNS, SORT)


def test_7b_tiny_board_has_empty_polls():
    # The French public board got only 2,652 votes, so most subdivisions are empty.
    long = mine.read_poll_by_poll(FRENCH)
    s = mine_metrics.summarize(long)
    assert s["winner"].isna().sum() == 1_149, "subdivisions where nobody voted"
    assert s["total"].sum() == 2_652


# ---------------------------------------------------------------- 8: All offices
def test_8a_sheet_with_six_races(same_rows):
    raw = pd.read_excel(ALL, sheet_name=0, header=None)
    cols = ["contest", "ward", "subdiv", "candidate", "votes"]
    rows = mine.parse_sheet(raw, "Ward 1")
    same_rows(rows, answer("all_offices_first_sheet"), cols, cols[:4])
    assert rows["contest"].nunique() == 6


def test_8a_whole_file():
    long = mine.read_poll_by_poll(ALL)
    assert long["votes"].sum() == 2_709_526
    assert long["contest"].nunique() == 31


def test_8b_list_contests(capsys):
    assert main([str(ALL), "--list"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 31 and "Mayor" in lines


def test_8b_pick_one_contest(tmp_path):
    out = tmp_path / "mayor"
    assert main([str(ALL), "--contest", "Mayor", "--csv-only", "--out", str(out)]) == 0
    table = pd.read_csv(out.with_suffix(".csv"))
    assert table["total"].sum() == 982_660, "same as the Mayor-only file"
    assert set(table["contest"]) == {"Mayor"}

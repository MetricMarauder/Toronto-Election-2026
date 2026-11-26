"""
Checkers for STEP 4 (practice/my_election_map/mapmaker.py).

A test can't judge whether a map LOOKS good. That part is you: open the
.html in a browser. These check the parts a computer can check.

Run:  python -m pytest practice -rs -k 4a      (or 4b, 4c)
Tip:  add --basetemp=practice_out to keep the test maps so you can open them.
"""
import pandas as pd
import pytest

from my_election_map import mapmaker as mine


# ---------------------------------------------------------------- 4a
def test_4a_top_three_and_other():
    winners = pd.Series(["Chow", "Chow", "Chow", "Bradford", "Bradford", "Saunders",
                         "Saunders", "Matlow", "Tie", None])
    out = mine.winner_groups(winners)
    assert isinstance(out, pd.Series)
    assert out.iloc[:7].tolist() == winners.iloc[:7].tolist(), "top 3 keep their names"
    assert out.iloc[7] == "Other or tie", "Matlow won only 1, so folds into Other"
    assert out.iloc[8] == "Other or tie", "a Tie is never one of the top 3"
    assert pd.isna(out.iloc[9]), "no votes stays missing"


def test_4a_real_mayor(joined):
    out = mine.winner_groups(joined["winner"])
    assert set(out.dropna()) == {"Chow Olivia", "Bradford Brad", "Other or tie"}


# ---------------------------------------------------------------- 4b
def test_4b_winner_map(joined, tmp_path):
    out = tmp_path / "winner.html"
    m = mine.make_map(joined, out=str(out))
    assert out.exists(), "make_map should save the file"
    assert hasattr(m, "save"), "return the folium Map"
    html = out.read_text()
    assert "leaflet" in html.lower()
    for name in ["Chow Olivia", "Bradford Brad", "Other or tie"]:
        assert name in html, f"{name!r} should appear in the legend"
    assert "#2a78d6" in html.lower(), "use CATEGORY_COLORS for the top 3"


# ---------------------------------------------------------------- 4c
@pytest.mark.parametrize("color", ["margin_pct", "total"])
def test_4c_amount_map(joined, tmp_path, color):
    out = tmp_path / f"{color}.html"
    mine.make_map(joined, out=str(out), color=color)
    assert out.exists()
    assert "leaflet" in out.read_text().lower()

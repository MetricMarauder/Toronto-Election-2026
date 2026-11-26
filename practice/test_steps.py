"""
Checks for practice/my_map.py.

    python -m pytest -rs -k step1      (or step2, step3, step4)
"""
from conftest import MAYOR
from my_map import step1_read_all_tabs, step2_summarize, step3_join, step4_map


def test_step1(answer_long, same_rows):
    long = step1_read_all_tabs(MAYOR)
    assert long["votes"].sum() == 982_660, "should match the city's official total"
    cols = ["ward", "subdiv", "candidate", "votes"]
    same_rows(long, answer_long, cols, cols[:3])


def test_step2(answer_long, answer_summary):
    s = step2_summarize(answer_long)
    assert len(s) == 1_431, "one row per subdivision"
    assert s["total"].sum() == 982_660
    mine = s.set_index(["ward", "subdiv"])
    correct = answer_summary.set_index(["ward", "subdiv"])
    clear = correct[correct["winner"] != "Tie"]          # ties: any winner is fine for now
    wrong = mine.loc[clear.index, "winner"] != clear["winner"]
    assert not wrong.any(), f"wrong winner in {wrong.sum()} subdivisions"


def test_step3(fake_shapes, answer_summary):
    gdf = step3_join(fake_shapes, answer_summary)
    assert len(gdf) == len(fake_shapes), "one row per shape"
    assert gdf["total"].notna().sum() == 1_348, "every shape should find its votes"
    row = gdf[gdf["AREA_LONG_CODE"] == "01001"].iloc[0]
    assert row["total"] == 466                           # ward 1, subdivision 1


def test_step4(joined, tmp_path):
    out = tmp_path / "map.html"
    step4_map(joined, out=str(out))
    assert out.exists(), "save the map to `out`"
    assert "leaflet" in out.read_text().lower()

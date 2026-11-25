"""
Checkers for STEP 5 (practice/my_election_map/cli.py).

Calling main([...]) with a list is exactly what typing the command does:
    my-election-map data/Poll_By_Poll_Mayor.xlsx --csv-only
is the same as
    main(["data/Poll_By_Poll_Mayor.xlsx", "--csv-only"])

Run:  python -m pytest practice -rs -k 5a      (or 5b)
"""
import pandas as pd
import pytest

from conftest import MAYOR
from my_election_map.cli import main


# ---------------------------------------------------------------- 5a
def test_5a_csv_only(tmp_path, capsys):
    out = tmp_path / "mayor"
    assert main([str(MAYOR), "--csv-only", "--out", str(out)]) == 0
    table = pd.read_csv(out.with_suffix(".csv"))
    assert len(table) == 1_431
    assert table["total"].sum() == 982_660
    assert "982,660" in capsys.readouterr().out, "print the summary line"


def test_5a_help_works(capsys):
    with pytest.raises(SystemExit):          # argparse prints help, then exits
        main(["--help"])
    assert "--csv-only" in capsys.readouterr().out


# ---------------------------------------------------------------- 5b
def test_5b_full_run(fake_shapes, tmp_path):
    shapes = tmp_path / "subdivisions.gpkg"
    fake_shapes.to_file(shapes)
    out = tmp_path / "mayor"
    assert main([str(MAYOR), "--boundaries", str(shapes), "--out", str(out)]) == 0
    assert out.with_suffix(".html").exists()


def test_5b_no_boundaries_is_a_clear_stop(tmp_path):
    with pytest.raises(SystemExit):
        main([str(MAYOR), "--out", str(tmp_path / "mayor")])

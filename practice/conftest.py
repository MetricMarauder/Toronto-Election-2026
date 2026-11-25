"""
Shared set-up for the practice checkers. You don't need to edit this file.

Two things happen here:
1. Fixtures: data every checker needs (the Mayor workbook, the finished tool's
   answers, fake boundary squares). pytest hands them to any test function
   that names them as an argument.
2. A friendly rule: if your function still says `raise NotImplementedError`,
   its checks show as SKIPPED ("not written yet") instead of FAILED.
   So a run of all the checkers doubles as a progress bar.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))           # so `tests.fake_boundaries` can be imported

DATA = ROOT / "data"
MAYOR = DATA / "Poll_By_Poll_Mayor.xlsx"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.when == "call" and call.excinfo is not None \
            and call.excinfo.errisinstance(NotImplementedError):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), item.location[1] or 0,
                           f"not written yet: {call.excinfo.value}")


# ---------------------------------------------------------------- fixtures
@pytest.fixture(scope="session")
def mayor_sheets():
    """Every sheet of the Mayor workbook, raw (header=None): {name: DataFrame}."""
    if not MAYOR.exists():
        pytest.skip(f"put the Poll_By_Poll_*.xlsx files in {DATA}/")
    return pd.read_excel(MAYOR, sheet_name=None, header=None)


@pytest.fixture(scope="session")
def answer_long():
    """The finished tool's long table for the Mayor file (Step 1's answer)."""
    from election_map.parse import read_poll_by_poll
    return read_poll_by_poll(MAYOR)


@pytest.fixture(scope="session")
def answer_summary(answer_long):
    """The finished tool's per-subdivision summary (Step 2's answer)."""
    from election_map.metrics import summarize
    return summarize(answer_long, compare=("Chow Olivia", "Bradford Brad"))


@pytest.fixture(scope="session")
def fake_shapes(answer_summary):
    """Fake square 'subdivisions', coded like the real layer: AREA_LONG_CODE = '01005'."""
    from tests.fake_boundaries import fake_boundaries
    return fake_boundaries(answer_summary)


@pytest.fixture
def same_rows():
    """Compare your table with the answer, ignoring row order and column order."""
    def check(mine, answer, columns, sort_by):
        missing = [c for c in columns if c not in mine.columns]
        assert not missing, f"your table is missing these columns: {missing}"
        assert len(mine) == len(answer), \
            f"your table has {len(mine):,} rows, the answer has {len(answer):,}"
        a = mine[columns].sort_values(sort_by).reset_index(drop=True)
        b = answer[columns].sort_values(sort_by).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b, check_dtype=False)
    return check

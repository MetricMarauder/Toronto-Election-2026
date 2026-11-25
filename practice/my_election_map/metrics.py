"""
STEP 2: Turn the long table into ONE ROW PER SUBDIVISION.

From this (one row per candidate):

    contest  ward  subdiv  candidate      votes
    Mayor    1     1       Bradford Brad  234
    Mayor    1     1       Chow Olivia    181
    Mayor    1     1       ...            ...

to this (one row per subdivision):

    contest  ward  subdiv  total  winner         runner_up    winner_pct  margin_pct
    Mayor    1     1       466    Bradford Brad  Chow Olivia  50.2        11.4

Rule: never type a candidate's name into this code. Generic columns like
"winner" work for ANY race: mayor, councillor, trustee.
"""
import pandas as pd

KEYS = ["contest", "ward", "subdiv"]    # the columns that identify one subdivision


# ---------------------------------------------------------------- Step 2a
def subdivision_totals(long: pd.DataFrame) -> pd.Series:
    """Total votes cast in each subdivision.

    Return a Series whose index is (contest, ward, subdiv) and whose
    values are the vote totals. Its name should be "total".
    """
    raise NotImplementedError("Step 2a: subdivision_totals")


# ---------------------------------------------------------------- Steps 2b, 2c, 2d
def summarize(long: pd.DataFrame, compare=None) -> pd.DataFrame:
    """One row per (contest, ward, subdiv).

    Step 2b. Columns: contest, ward, subdiv, total, winner, runner_up,
             winner_pct, margin_pct
        winner_pct = winner's votes / total * 100, rounded to 1 decimal
        margin_pct = (winner's votes - runner-up's votes) / total * 100, rounded to 1 decimal

    Step 2c. Be honest about edge cases:
        top two candidates have the same votes -> winner is "Tie"
        nobody voted (total == 0)              -> winner is None, and
                                                  winner_pct, margin_pct are NaN

    Step 2d. If compare=("Name A", "Name B"), also add:
        a_pct, b_pct   each one's share of the vote, rounded to 1 decimal
        a_minus_b      a_pct - b_pct, rounded to 1 decimal (positive = A ahead)
    """
    raise NotImplementedError("Step 2b: summarize")

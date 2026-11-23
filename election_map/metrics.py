"""
STEP 2 — Turn long vote rows into one summary row per subdivision.

The trick that makes this reusable: never write candidate names into the code.
Instead compute generic columns that make sense for ANY race:

  total       votes cast in the subdivision
  winner      top candidate ("Tie" if the top two are equal)
  runner_up   second place
  winner_pct  winner's share of the vote, 0-100
  margin_pct  winner's share minus runner-up's share (how close it was)

For a two-way race you often want a signed map (blue = A, red = B).
Pass compare=("Candidate A", "Candidate B") and you also get
  a_pct, b_pct, a_minus_b   (positive = A ahead)
"""
import pandas as pd

KEYS = ["contest", "ward", "subdiv"]


def summarize(long: pd.DataFrame, compare=None, contest=None) -> pd.DataFrame:
    """One row per (contest, ward, subdiv). See module docstring for columns."""
    if contest is not None:
        long = long[long["contest"] == contest]
        if long.empty:
            raise ValueError(f"No rows for contest {contest!r}")

    # Sort so that inside each subdivision the biggest vote-getter comes first.
    ranked = long.sort_values(KEYS + ["votes"], ascending=[True, True, True, False])
    groups = ranked.groupby(KEYS, sort=False)

    first = groups.nth(0).set_index(KEYS)      # top candidate per subdivision
    second = groups.nth(1).set_index(KEYS)     # second place
    total = groups["votes"].sum()

    out = pd.DataFrame({"total": total})
    out["winner"] = first["candidate"]
    out["runner_up"] = second["candidate"]
    top = first["votes"]
    nxt = second["votes"].reindex(out.index).fillna(0)
    out["winner_pct"] = (top / out["total"] * 100).round(1)
    out["margin_pct"] = ((top - nxt) / out["total"] * 100).round(1)

    # Ties and empty polls: say so instead of pretending someone won.
    out.loc[top == nxt, "winner"] = "Tie"
    empty = out["total"] == 0
    out.loc[empty, "winner"] = None
    out.loc[empty, ["winner_pct", "margin_pct"]] = float("nan")   # keep these columns numeric

    if compare:
        a, b = compare
        votes = long.pivot_table(index=KEYS, columns="candidate", values="votes", aggfunc="sum")
        for name in (a, b):
            if name not in votes.columns:
                raise ValueError(f"Candidate {name!r} not found. Try one of: {sorted(votes.columns)[:10]}")
        out["a_pct"] = (votes[a] / out["total"] * 100).round(1)
        out["b_pct"] = (votes[b] / out["total"] * 100).round(1)
        out["a_minus_b"] = (out["a_pct"] - out["b_pct"]).round(1)

    return out.reset_index()


def check_against_sheet(long: pd.DataFrame, summary: pd.DataFrame) -> None:
    """Cheap sanity check: totals must survive the reshape unchanged."""
    if long["votes"].sum() != summary["total"].sum():
        raise AssertionError("Vote totals changed during summarize() — something is wrong")

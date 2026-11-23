"""
STEP 1 — Read the raw Excel files into one tidy ("long") table.

Toronto's poll-by-poll workbooks look friendly to a human but awkward to code:
one sheet per ward, candidates down the side, subdivisions across the top.
And the layout varies between files:

  Mayor / Councillor    one block per sheet, with an office row ("Mayor")
  School boards         several blocks per sheet, one per *city* ward the
                        school ward overlaps
  All_Offices           several races stacked in one sheet

Instead of writing a parser for each file, we read every sheet top to bottom
and react to what each row *is*. That's called a state machine:

  "Subdivision" row       -> new block starts; remember which column = which subdivision
  label row, no numbers   -> a contest title ("Mayor", "Trustee, ...")
  label row with numbers  -> a candidate's votes
  "City Ward N Totals"    -> block ends; now we know the city ward, and we can
                             CHECK our numbers against the official totals

The output is "long" data: one row per (contest, ward, subdivision, candidate).
Long data is the shape that pandas, groupby, and pivot all expect.
"""
import re
from pathlib import Path

import pandas as pd

TOTALS_RE = re.compile(r"City Ward\s+(\d+)\s+Totals", re.IGNORECASE)


class ParseError(Exception):
    """Raised when the numbers we read don't add up to the official totals."""


def _is_number(value) -> bool:
    # Excel cells arrive as floats, ints, strings or NaN. NaN is a float, so check it too.
    return isinstance(value, (int, float)) and not pd.isna(value)


def _clean_contest(title: str) -> str:
    # "City Ward 1 Etobicoke North" is a place, not a contest -> caller ignores it.
    return " ".join(str(title).split())


def parse_sheet(raw: pd.DataFrame, sheet_name: str, check_totals: bool = True) -> pd.DataFrame:
    """Turn ONE sheet (read with header=None) into long rows."""
    rows = []
    contest = sheet_name          # fallback if the sheet never names its contest
    columns = {}                  # column index -> subdivision number
    pending = []                  # candidate rows waiting for their "Totals" line

    for i in range(len(raw)):
        label = raw.iat[i, 0]
        cells = raw.iloc[i, 1:]

        if pd.isna(label):
            continue                                   # blank spacer row
        label = str(label).strip()

        # 1) Header row: build the column -> subdivision lookup for this block.
        if label.lower() == "subdivision":
            columns = {}
            for col, value in cells.items():
                if _is_number(value):
                    columns[col] = int(value)
                elif str(value).strip().isdigit():     # some files store 99 as text
                    columns[col] = int(str(value).strip())
                # "Total" and empty cells are skipped on purpose
            continue

        # 2) Totals row: close the block, stamp the ward, verify.
        match = TOTALS_RE.match(label)
        if match:
            ward = int(match.group(1))
            if check_totals:
                for col, subdiv in columns.items():
                    ours = sum(r["votes"] for r in pending if r["subdiv"] == subdiv)
                    official = raw.iat[i, col]
                    if _is_number(official) and ours != int(official):
                        raise ParseError(
                            f"{sheet_name}, ward {ward}, subdivision {subdiv}: "
                            f"we counted {ours} but the sheet says {int(official)}"
                        )
            for r in pending:
                r["ward"] = ward
            rows.extend(pending)
            pending = []
            continue

        # 3) Label with no numbers anywhere: it's a title.
        if not any(_is_number(v) for v in cells):
            if not label.lower().startswith("city ward"):
                contest = _clean_contest(label)
            continue

        # 4) Otherwise it's a candidate row.
        for col, subdiv in columns.items():
            value = raw.iat[i, col]
            pending.append({
                "contest": contest,
                "subdiv": subdiv,
                "candidate": label,
                "votes": int(value) if _is_number(value) else 0,
            })

    if pending:
        raise ParseError(f"{sheet_name}: a block never reached its 'City Ward N Totals' row")
    return pd.DataFrame(rows)


def read_poll_by_poll(path, check_totals: bool = True) -> pd.DataFrame:
    """Read every sheet of a poll-by-poll workbook into one long DataFrame.

    Columns: source, sheet, contest, ward, subdiv, candidate, votes
    """
    path = Path(path)
    sheets = pd.read_excel(path, sheet_name=None, header=None)   # dict: name -> DataFrame
    frames = []
    for name, raw in sheets.items():
        df = parse_sheet(raw, name, check_totals=check_totals)
        df.insert(0, "sheet", name)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out.insert(0, "source", path.name)
    return out[["source", "sheet", "contest", "ward", "subdiv", "candidate", "votes"]]

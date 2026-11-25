"""
STEP 1: Read the raw Excel sheets into one long table.

Each sheet looks like this (read with header=None, so nothing is hidden):

    row  column 0                      column 1  column 2  ...  last column
    0    City Ward 1 Etobicoke North   NaN       NaN
    1    Subdivision                   1.0       3.0       ...  Total
    2    Mayor                         NaN       NaN
    3    Abdulkadir Imad               2.0       3.0       ...  290
    ...  (one row per candidate)
    56   City Ward 1 Totals            466.0     935.0     ...

You'll turn it into a "long" table with ONE ROW PER (contest, ward,
subdivision, candidate):

    contest  ward  subdiv  candidate         votes
    Mayor    1     1       Abdulkadir Imad   2
    Mayor    1     3       Abdulkadir Imad   3
    ...

Work through the functions in order: 1a, 1b, 1c, ... Each one is small.
After each, run its checker:   python -m pytest practice -rs -k 1a
"""
import re
from pathlib import Path

import pandas as pd


class ParseError(Exception):
    """Raise this when your numbers don't add up to the sheet's official totals."""


# ---------------------------------------------------------------- Step 1a
def is_number(value) -> bool:
    """True if an Excel cell holds a real number, False otherwise.

    Excel cells arrive in Python as int, float, str, or NaN ("Not a Number",
    pandas' way of saying "empty cell").

        is_number(3)       -> True
        is_number(466.0)   -> True
        is_number(float("nan"))  -> False   (empty cell)
        is_number("Total") -> False
        is_number(None)    -> False
    """
    raise NotImplementedError("Step 1a: is_number")


# ---------------------------------------------------------------- Step 1b
def subdivision_columns(cells: pd.Series) -> dict:
    """Read a "Subdivision" header row and say which column is which subdivision.

    `cells` is the row WITHOUT its first cell, e.g. raw.iloc[1, 1:].
    Its index is the column numbers, its values are what's in each cell:

        index:   1     2     3    ...  46     47
        value:   1.0   3.0   5.0  ...  99.0   "Total"

    Return a dict {column number: subdivision number}, skipping anything
    that isn't a subdivision (like "Total" or an empty cell):

        {1: 1, 2: 3, 3: 5, ..., 46: 99}

    Watch out: some files store a subdivision as text, like "99".
    """
    raise NotImplementedError("Step 1b: subdivision_columns")


# ---------------------------------------------------------------- Step 1c
def ward_from_totals(label: str):
    """If `label` is a totals row, return its ward number. Otherwise None.

        ward_from_totals("City Ward 1 Totals")   -> 1
        ward_from_totals("City Ward 25 Totals")  -> 25
        ward_from_totals("City Ward 1 Etobicoke North") -> None   (a title, not totals)
        ward_from_totals("Chow Olivia")           -> None
    """
    raise NotImplementedError("Step 1c: ward_from_totals")


# ---------------------------------------------------------------- Steps 1d + 1e
def parse_sheet(raw: pd.DataFrame, sheet_name: str, check_totals: bool = True) -> pd.DataFrame:
    """Turn ONE sheet (read with header=None) into long rows.

    Return a DataFrame with columns: contest, ward, subdiv, candidate, votes

    Step 1d: walk down the rows one at a time and decide what each row IS:
        empty first cell            -> skip it
        "Subdivision"               -> a new block starts (use subdivision_columns)
        "City Ward N Totals"        -> the block ends (use ward_from_totals);
                                       now you know the ward for every row
                                       you collected since the block started
        a label with no numbers     -> a contest title, like "Mayor"
                                       (but NOT "City Ward 1 Etobicoke North")
        a label with numbers        -> a candidate: one output row per subdivision

    Step 1e: when you reach a Totals row and check_totals is True, add up
    your own votes for each subdivision and compare with the Totals row.
    If any number disagrees, raise ParseError with a helpful message.
    Ignore check_totals in 1d; come back to it in 1e.
    """
    raise NotImplementedError("Step 1d: parse_sheet")


# ---------------------------------------------------------------- Step 1f
def read_poll_by_poll(path, check_totals: bool = True) -> pd.DataFrame:
    """Read EVERY sheet of a workbook into one long DataFrame.

    Columns, in this order: source, sheet, contest, ward, subdiv, candidate, votes
        source = the file's name, e.g. "Poll_By_Poll_Mayor.xlsx"
        sheet  = the sheet's name, e.g. "Ward 1"
    """
    raise NotImplementedError("Step 1f: read_poll_by_poll")

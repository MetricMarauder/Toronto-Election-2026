# Learning path: from spreadsheet to map

You asked to learn this, not just run it. This file is a reading order for the code, with small exercises. Do them in a notebook (`jupyter lab`, then open `notebooks/walkthrough.ipynb`), where you can run one line at a time and look at the result.

The pipeline is four steps. Each file does one job:

```
Excel  --parse.py-->  long table  --metrics.py-->  1 row per subdivision
                                                          |
boundaries  --geo.py (load + join)-----------------------+
                                                          |
                                         mapmaker.py --> map.html / map.png
__main__.py wires them together as one command.
```

A rule worth keeping: **each step's output is a table you can open and inspect.** When something goes wrong, find the first step whose output looks wrong.

---

## Step 0: Look before you code

Before writing any parsing code, look at the raw data with pandas:

```python
import pandas as pd
raw = pd.read_excel("data/Poll_By_Poll_TDSB.xlsx", sheet_name="Ward 1", header=None)
raw
```

`header=None` tells pandas not to guess at headers, so you see exactly what's in the file. Notice that this sheet holds **two blocks** (city wards 1 and 7), because school wards don't line up with city wards. A Mayor sheet has one block, and All_Offices has six. That's why the parser works the way it does.

**Exercise 0:** Open the Councillor file's Ward 1 sheet. Which row says which race it is? Where are the totals?

## Step 1: Parsing (`parse.py`)

Read `parse_sheet()`. It's a **state machine**: it walks down the rows and decides what each row *is*, using four rules. The variables `columns`, `contest`, and `pending` are its memory between rows.

Key ideas:
* **Long format.** The output has one row per (contest, ward, subdivision, candidate). Wide spreadsheets are for people to read; long tables are what code works best with.
* **Check against the source.** Every block ends at a "City Ward N Totals" row, and the parser adds up its own numbers and compares. That's how you know the parse is right, rather than just hoping.

**Exercise 1:** `long = read_poll_by_poll("data/Poll_By_Poll_Mayor.xlsx")`. Then:
* `long.groupby("candidate").votes.sum().sort_values(ascending=False).head()`, which shows the citywide result.
* `long.groupby("ward").votes.sum()`, the votes per ward.

**Exercise 2:** Break it on purpose. In a notebook, copy one sheet, change one number with `raw.iat[5, 3] = 999`, and run `parse_sheet(raw, "test")`. Read the error you get. Good tools fail loudly.

## Step 2: Summarizing (`metrics.py`)

`summarize()` turns the long table into one row per subdivision with **generic** columns: `winner`, `runner_up`, `winner_pct`, `margin_pct`. No candidate names are written into the code, which is why the same function works for Mayor, Councillor, and trustee races.

Key ideas:
* `sort_values` followed by `groupby(...).nth(0)` gives "first place in each group". Read the code line by line in a notebook and look at `first` and `second`.
* Edge cases are part of the job: ties (11 subdivisions in the mayor race) and empty polls (0 votes) get handled explicitly.

**Exercise 3:** Which 10 subdivisions were closest between Chow and Bradford?
```python
s = summarize(long, compare=("Chow Olivia", "Bradford Brad"))
s.assign(gap=s.a_minus_b.abs()).sort_values("gap").head(10)
```

**Exercise 4:** Add a `turnout_rank` column (1 = most votes cast) to `summarize()`. Hint: `out["total"].rank(ascending=False)`. Then run the tests.

## Step 3: Boundaries and the join (`geo.py`)

A GeoDataFrame is a pandas table with a `geometry` column holding the shapes. Joining is an ordinary `merge` on a key column. The hard part is that the two sides write the key differently.

Key ideas:
* **Don't guess the key; measure it.** `detect_key()` tries every column against every format in `KEY_FORMATS` and keeps the best match rate. This replaces squinting at attribute tables in QGIS.
* **`merge(..., indicator=True)`** labels every row `both`, `left_only`, or `right_only`. That's your join report. In QGIS a failed join just looks like "one color"; here you get numbers.
* `to_crs(4326)` converts the shapes to latitude/longitude, which web maps expect. (Your QGIS project uses EPSG:3857, the same "web Mercator" OpenStreetMap uses for display.)

**Exercise 5:** Load your real boundaries and look at them:
```python
from election_map.geo import load_boundaries, detect_key
shapes = load_boundaries("data/subdivisions.gpkg")
shapes.head(); shapes.plot()
detect_key(shapes, summarize(long))
```

**Exercise 6:** The tests caught a real bug while this was being built. With a single ward, a counter column (`OBJECTID`) matched by coincidence. Read `test_one_ward_does_not_fool_key_detection` and the fix in `detect_key`. Every bug you fix deserves a test like that.

## Step 4: The map (`mapmaker.py`)

`gdf.explore()` builds a Leaflet web map. Most of the code is about **color**, and the rules are worth learning:
* **Categories** (who won): distinct hues, but at most 3 on a filled map. Touching shapes in 4+ hues become hard to tell apart, especially for colorblind readers.
* **One-sided amounts** (margin, turnout): one hue, light to dark.
* **Two-sided amounts** (A minus B): two hues with **gray at zero**, and a symmetric scale (−50 to +50), so gray really means "even".

**Exercise 7:** Make a turnout map: `election-map data/Poll_By_Poll_Mayor.xlsx --boundaries data/subdivisions.gpkg --color total`. What's misleading about it? (Hint: big subdivisions have more voters. Counts usually need dividing by something.)

## Step 5: Making it a tool (`__main__.py`, `pyproject.toml`)

* `argparse` turns options into a command line with a free `--help`.
* `pyproject.toml` plus `pip install -e .` makes `election-map` work from any folder. The `-e` means your code edits take effect immediately.
* The tests in `tests/` run on fake square shapes (`tests/fake_boundaries.py`), so they work offline in seconds.

**Exercise 8 (reuse):** Next election, check whether the files still parse: run `election-map NEW_FILE.xlsx --csv-only`. If the layout changed, the totals check tells you where.

## Where to go next

* Put two maps side by side, such as 2023 vs 2026 for the same subdivisions, to see how areas changed.
* Learn `plotly.express.choropleth_map` for maps with sliders and dropdowns.
* Read *Python for Data Analysis* by Wes McKinney (the author of pandas), chapters 5–10.

# Build it yourself: election_map, step by step

You'll rewrite the whole tool, one small function at a time, in your own folder:

```
practice/my_election_map/      <- YOU write the code here (every function is empty)
practice/test_step*.py         <- checkers that tell you when each step is right
election_map/                  <- the finished, working version: your answer key
```

**How each step works**

1. **Read** the step below and the function's description in its file.
2. **Try it** in a notebook first, one line at a time (`jupyter lab`).
3. **Write** the function. Delete the `raise NotImplementedError(...)` line.
4. **Check** it: `python -m pytest practice -rs -k 1a` (swap in the step's code).
5. **Commit** when it passes (see "Saving your progress").

Stuck? Open the **Hints**, one at a time. Still stuck? Read the matching function in
`election_map/`, close it, and write yours from memory. That's still learning.

**See your progress any time:**

```bash
python -m pytest practice -rs
```

Steps you haven't done show as `SKIPPED ... not written yet`. Done steps show as passed.
Something written but wrong shows as `FAILED`, with a message saying what's off.

---

## Setup (one time, on your Mac)

```bash
cd election_map
git fetch origin
git switch learn/build-it-yourself
source .venv/bin/activate
pip install -e ".[dev]"
```

The last line matters: it registers your `my_election_map` package and the
`my-election-map` command. Check it worked:

```bash
python -m pytest practice -rs
```

You should see `45 skipped`. That's your starting line.

## Saving your progress

After each step passes:

```bash
git add practice
git commit -m "Step 1a: is_number"
git push
```

The first time, use `git push -u origin learn/build-it-yourself`. After that, plain
`git push` is enough. Each commit is a checkpoint you can return to, and GitHub
shows your progress.

---

## The big picture

```
Excel sheets ──Step 1──▶ long table ──Step 2──▶ one row per subdivision
                                                        │
boundary shapes ──Step 3 (load + join)─────────────────┘
                                                        │
                                   Step 4 ──▶ map.html
              Step 5 wires it all into one command: my-election-map
```

Every step's output is a table you can look at. When something goes wrong, find
the first step whose table looks wrong.

---

## Step 0: Look before you code (no code yet)

In a notebook:

```python
import pandas as pd
raw = pd.read_excel("data/Poll_By_Poll_Mayor.xlsx", sheet_name="Ward 1", header=None)
raw
```

`header=None` means "don't guess which row is the header, show me everything."

Answer these on paper before going on:
- Which row says **Subdivision**? What's in the last column of that row?
- Which row is the **contest title**? How is it different from a candidate row?
- What's in the last row?

Now look at `Poll_By_Poll_TDSB.xlsx`, sheet `Ward 1`. How many "City Ward N Totals"
rows does it have? Your parser has to handle both layouts.

---

## Step 1: Parsing (`practice/my_election_map/parse.py`)

### 1a. `is_number(value)` (warm-up)

Return True only for real numbers. The catch: pandas shows an empty cell as
`NaN`, and `NaN` *is* a float.

**Try in the notebook:** `type(raw.iat[0, 1])`, `type(raw.iat[1, 1])`, `type(raw.iat[1, 47])`

<details><summary>Hint 1</summary>

`isinstance(value, (int, float))` asks "is it an int or a float?"
</details>
<details><summary>Hint 2</summary>

`pd.isna(value)` is True for NaN. Combine the two checks with `and not`.
</details>

Check: `python -m pytest practice -rs -k 1a`

### 1b. `subdivision_columns(cells)`

Turn the header row into a lookup: "column 2 holds subdivision 3." You'll need this
for every candidate row.

**New idea: a dictionary.** `{1: 1, 2: 3}` maps keys to values. Build one with
`d = {}` and then `d[key] = value` inside a loop.

**Try:** `cells = raw.iloc[1, 1:]`, then `for col, value in cells.items(): print(col, value)`

<details><summary>Hint 1</summary>

Use your own `is_number` from 1a. Remember `int(5.0)` gives `5`.
</details>
<details><summary>Hint 2</summary>

For text like `" 99 "`: `str(value).strip()` removes the spaces, and `.isdigit()` says
whether what's left is all digits.
</details>

### 1c. `ward_from_totals(label)`

**New idea: a regular expression (regex),** a pattern for matching text.
`r"City Ward\s+(\d+)\s+Totals"` reads as: "City Ward", some spaces, *one or more
digits (captured)*, some spaces, "Totals".

**Try:**
```python
import re
m = re.match(r"City Ward\s+(\d+)\s+Totals", "City Ward 7 Totals")
m, m.group(1)
re.match(r"City Ward\s+(\d+)\s+Totals", "Chow Olivia")   # what comes back?
```

<details><summary>Hint</summary>

If `m` is None, return None. Otherwise return `int(m.group(1))`.
</details>

### 1d. `parse_sheet(raw, sheet_name)`: the big one

This is a **state machine**. You walk down the rows, and a few variables remember
things between rows:

```python
rows = []          # finished output rows
contest = sheet_name   # the current race (updated when you see a title row)
columns = {}       # the current column -> subdivision lookup (from 1b)
pending = []       # candidate rows waiting to learn their ward
```

For each row, decide what it **is**, in this order:

| The first cell is... | So the row is... | Do this |
|---|---|---|
| empty (NaN) | a spacer | `continue` (skip) |
| `"Subdivision"` | a header | `columns = subdivision_columns(...)` |
| `"City Ward N Totals"` | the end of a block | set `ward = N` on every pending row, move them to `rows`, empty `pending` |
| text, and no numbers on the row | a title | if it doesn't start with "City Ward", it's the contest |
| text, with numbers | a candidate | one `pending` row per subdivision in `columns` |

**Why "pending"?** You don't learn the ward until the *bottom* of the block, so
candidate rows wait there until the Totals row arrives.

Each output row is a dict:
`{"contest": ..., "ward": ..., "subdiv": ..., "candidate": ..., "votes": ...}`.
At the end, `pd.DataFrame(rows)` turns the list of dicts into a table.

**Try it a piece at a time:**
```python
for i in range(8):
    print(i, raw.iat[i, 0], raw.iloc[i, 1:4].tolist())
```

<details><summary>Hint 1: the loop</summary>

```python
for i in range(len(raw)):
    label = raw.iat[i, 0]
    cells = raw.iloc[i, 1:]
    if pd.isna(label):
        continue
    label = str(label).strip()
    ...
```
</details>
<details><summary>Hint 2: "no numbers on the row"</summary>

`any(is_number(v) for v in cells)` is True if at least one cell is a number.
</details>
<details><summary>Hint 3: a candidate row</summary>

Loop over `columns.items()`. That gives you each column and its subdivision. The vote
count is `raw.iat[i, col]`. If it isn't a number, count it as 0.
</details>

Check: `python -m pytest practice -rs -k 1d`. Three checks: one mayor sheet, a
school-board sheet with two blocks, and an all-offices sheet with six races.
If only the last two fail, look at how you reset things between blocks.

### 1e. Check your work against the sheet

At each Totals row, add up *your* votes for each subdivision and compare them with
the number on the Totals row. If they disagree, `raise ParseError(...)` with a message
that names the ward and subdivision. Only do this when `check_totals` is True.

This is the most important idea in the project: **don't hope the parse is
right, prove it** against numbers the city published.

<details><summary>Hint</summary>

`sum(r["votes"] for r in pending if r["subdiv"] == subdiv)` is your count. The
official count is `raw.iat[i, col]` on the Totals row.
</details>

### 1f. `read_poll_by_poll(path)`

`pd.read_excel(path, sheet_name=None, header=None)` gives you a **dict of every
sheet**: `{"Ward 1": DataFrame, "Ward 2": ...}`. Parse each sheet, add `sheet` and
`source` columns, and stack them with `pd.concat(list_of_tables, ignore_index=True)`.

<details><summary>Hint</summary>

`Path(path).name` gives the file name without its folders. To put columns in
order: `df[["source", "sheet", ...]]`.
</details>

**Milestone:** `mine.read_poll_by_poll("data/Poll_By_Poll_Mayor.xlsx").votes.sum()`
gives **982,660**, the official total. You just wrote a verified Excel parser.

---

## Step 2: Summarizing (`practice/my_election_map/metrics.py`)

The checkers give your functions the *answer key's* long table, so Step 2 works
even if Step 1 still has a bug.

### 2a. `subdivision_totals(long)`

**New idea: groupby.** "Split the table into groups, do something to each, then
combine the results." Here, `long.groupby(["contest", "ward", "subdiv"])["votes"]`,
followed by `.sum()`.

**Try:** `long.groupby("candidate")["votes"].sum().sort_values()` gives the citywide result.

<details><summary>Hint</summary>

`.rename("total")` names the resulting Series.
</details>

### 2b. `summarize(long)`: winner, runner-up, percentages

The trick: **sort first, then take positions.** Sort by subdivision, and by votes from
highest to lowest. Then in each group, row 0 is the winner and row 1 is the
runner-up.

**Try:**
```python
ranked = long.sort_values(["contest", "ward", "subdiv", "votes"],
                          ascending=[True, True, True, False])
groups = ranked.groupby(["contest", "ward", "subdiv"])
groups.nth(0).head()     # winners
groups.nth(1).head()     # runners-up
```

<details><summary>Hint 1</summary>

`.set_index(KEYS)` on `nth(0)` and `nth(1)` makes them line up with your totals
from 2a. Then build: `out = pd.DataFrame({"total": totals})`, followed by
`out["winner"] = first["candidate"]`, and so on.
</details>
<details><summary>Hint 2</summary>

`(top / out["total"] * 100).round(1)`. At the end, `out.reset_index()` turns the
index back into ordinary columns.
</details>

### 2c. Ties and empty polls

The real data has **11 mayor ties**. If your code takes "row 0" blindly, it hands
the win to whoever is listed first, which is the alphabet, not the voters.

- Where the top two have equal votes: `winner = "Tie"`
- Where `total == 0`: `winner = None`, and the percentages are `float("nan")`

**New idea: `.loc` with a True/False mask.** `out.loc[mask, "winner"] = "Tie"` changes
only the rows where the mask is True.

**Milestone:** Chow 1,014, Bradford 406, Tie 11.

### 2d. Head to head: `compare=("A", "B")`

**New idea: pivot_table,** which turns long data back into wide data: one column per
candidate.

**Try:** `long.pivot_table(index=KEYS, columns="candidate", values="votes", aggfunc="sum")`

Then `a_pct = votes[a] / total * 100`, and the same for `b_pct`.
`a_minus_b = a_pct - b_pct`. Round each to 1 decimal.

---

## Step 3: Boundaries and the join (`practice/my_election_map/geo.py`)

A **GeoDataFrame** is a pandas table with a `geometry` column holding a shape in
each row.

### 3a. `make_key(ward, subdiv)`

The city's layer writes ward 1, subdivision 5 as `"01005"`. We confirmed this on your
first real run.

**New idea: format codes in f-strings.** `f"{7:02d}"` gives `"07"`: pad to 2 digits
with zeros.

### 3b. `load_boundaries(source)`

`gpd.read_file(path)` reads .gpkg, .shp and .geojson files. `.to_crs(4326)` converts
the shapes to latitude/longitude. Use `Path(source).exists()` to check the file is there.

**Try:** load your QGIS export (see the README for how), then call `.head()`, `.plot()` and `.crs`.

### 3c. `join(shapes, summary)`

1. Add a `key` column to `summary` with `make_key` for every row.
2. Put the boundary's `AREA_LONG_CODE` into a `key` column too.
3. Merge them with **`how="outer", indicator=True`**.

**New idea: indicator=True.** It adds a `_merge` column that labels every row
`both`, `left_only` (a shape with no results) or `right_only` (results with no
shape). That column *is* your join report: count each label.

In QGIS, a failed join just looks like "everything is one color." Here you get numbers.

<details><summary>Hint</summary>

Keep the rows that have a shape: `merged[merged["_merge"] != "right_only"]`. Wrap
the result back up: `gpd.GeoDataFrame(that, geometry="geometry", crs=shapes.crs)`.
</details>

**Milestone with real data:** `1356/1356 shapes matched`, and 75 results without shapes
(the advance and mail polls).

---

## Step 4: The map (`practice/my_election_map/mapmaker.py`)

### 4a. `winner_groups(winners)`

Keep the top 3 winners and fold everyone else into "Other or tie". Why only 3?
Neighbouring shapes in 4 or more colors are hard to tell apart, especially for
colorblind readers.

<details><summary>Hint</summary>

`winners[winners != "Tie"].value_counts()` lists candidates from most wins to
fewest. Take `.index[:3]`. Then `winners.where(winners.isin(top), "Other or tie")`.
Put back the missing values at the end.
</details>

### 4b. `make_map(gdf)`: the winner map

```python
m = gdf.explore(column="Winner", categorical=True, categories=[...],
                cmap=[...colors...], legend=True, tooltip=[...], tiles="OpenStreetMap")
m.save(out)
```

Open the result in your browser. **Does it look right?** That check is yours; a test
can't do it.

### 4c. Amount maps

For `margin_pct` or `total`, use one hue from light to dark: `cmap="Blues"`, no `categorical`.

Then make a `total` map and ask: *what's misleading about it?*
(Big subdivisions have more voters. A raw count usually needs dividing by something.)

---

## Step 5: One command (`practice/my_election_map/cli.py`)

### 5a. `argparse`: options and `--csv-only`

```python
p = argparse.ArgumentParser(description="...")
p.add_argument("results")                      # required, no dashes
p.add_argument("--out", default="map")
p.add_argument("--csv-only", action="store_true")
args = p.parse_args(argv)                      # args.results, args.out, args.csv_only
```

You get `--help` for free. Try `my-election-map --help`.

### 5b. The whole pipeline

Chain your steps: parse, summarize, CSV, load boundaries, join, print the report, make the map.
If `--boundaries` is missing, `sys.exit("a helpful message")`.

**Final milestone:**

```bash
my-election-map data/Poll_By_Poll_Mayor.xlsx --boundaries data/subdivisions.gpkg --out my_mayor
```

Open `my_mayor.html`. You built that, every line of it. 🎉

```bash
python -m pytest practice -rs      # 45 passed
```

---

## After that: make it yours

These aren't in the finished tool either, so there's no answer key:

1. **Turnout rank:** add a `turnout_rank` column to `summarize` (1 = most votes).
2. **The `--ward` option:** map just one ward's councillor race.
3. **2023 vs 2026:** two summaries for the same subdivisions, and a map of the change.
   Write the test first, describing what "right" looks like, then the code.

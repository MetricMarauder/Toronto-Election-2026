# Build it yourself

You'll rebuild this tool one small function at a time, starting from the city's raw
spreadsheets (`data/*.xlsx`).

- **Part 1:** the Mayor race, all the way to a map.
- **Part 2:** the smaller races: Councillor, school boards, and the all-offices file.

| Folder | What's in it |
|---|---|
| `practice/my_election_map/` | **Your code.** Every function is empty and says what it should do. |
| `practice/answers/` | The correct results the checkers compare yours with. |

The finished, working code is on the `main` branch, not this one. Peek at it on GitHub only when you're stuck.

## Setup (once)

```bash
git switch learn/build-it-yourself
source .venv/bin/activate
pip install -e ".[dev]"
```

## For every step

1. Try it in a notebook (`jupyter lab`).
2. Write the function, and delete its `raise NotImplementedError` line.
3. Check it: `python -m pytest practice -rs -k 1a` (use the step's code in place of `1a`).
4. Save it: `git add practice && git commit -m "1a" && git push`

To see all your progress: `python -m pytest practice -rs`. "SKIPPED" means not written yet.

---

## Part 1: Mayor, start to finish

**Step 0. Look first.** Run this in a notebook and find the Subdivision row, the contest title and the Totals row:
```python
import pandas as pd
pd.read_excel("data/Poll_By_Poll_Mayor.xlsx", sheet_name="Ward 1", header=None)
```

### Step 1: Read the spreadsheet (`parse.py`)

| Code | Function | Does |
|---|---|---|
| 1a | `is_number` | True for a real number, False for text or an empty cell |
| 1b | `subdivision_columns` | Header row → `{column: subdivision}` |
| 1c | `ward_from_totals` | `"City Ward 7 Totals"` → `7` |
| 1d | `parse_sheet` | One sheet → one row per subdivision per candidate |
| 1e | (same function) | Check your sums against the Totals row |
| 1f | `read_poll_by_poll` | Every sheet → one table |

<details><summary>Hints</summary>

- 1a: `isinstance(v, (int, float))` and `pd.isna(v)`
- 1c: `re.match(r"City Ward\s+(\d+)\s+Totals", label)`
- 1d: loop over rows and decide what each one is: blank, Subdivision, Totals, title or candidate.
  Keep candidate rows in a `pending` list until the Totals row tells you the ward.
- 1f: `pd.read_excel(path, sheet_name=None, header=None)` gives every sheet, then use `pd.concat`.
</details>

✅ Your total is **982,660 votes**, the same as the city's official count.

### Step 2: One row per subdivision (`metrics.py`)

| Code | Does |
|---|---|
| 2a | Total votes per subdivision |
| 2b | Winner, runner-up, winner's %, margin % |
| 2c | Ties say "Tie", and empty polls have no winner |
| 2d | Head to head: `compare=("Chow Olivia", "Bradford Brad")` |

<details><summary>Hints</summary>

- 2a: `long.groupby(["contest", "ward", "subdiv"])["votes"].sum()`
- 2b: sort by votes from high to low, then `groupby(...).nth(0)` is the winner and `.nth(1)` the runner-up
- 2c: `out.loc[mask, "winner"] = "Tie"`
- 2d: `long.pivot_table(index=..., columns="candidate", values="votes")`
</details>

✅ Chow won **1,014** subdivisions, Bradford **406**, and **11** were ties.

### Step 3: Attach votes to shapes (`geo.py`)

| Code | Does |
|---|---|
| 3a | `make_key(1, 5)` → `"01005"`, the way the city's map layer writes it |
| 3b | Load a boundary file, in latitude/longitude |
| 3c | Join the votes to the shapes, and count what matched |

<details><summary>Hints</summary>

- 3a: `f"{ward:02d}{subdiv:03d}"`
- 3b: `gpd.read_file(path).to_crs(4326)`
- 3c: `merge(..., how="outer", indicator=True)`, then count the `_merge` column
</details>

Get the real boundaries first: in QGIS, right-click your *Voting Subdivision 2026* layer, choose **Export → Save Features As…**, set Format to **GeoPackage**, and save it as `data/subdivisions.gpkg`.

✅ On the real boundaries: **1,356 of 1,356** shapes matched.

### Step 4: Draw the map (`mapmaker.py`)

| Code | Does |
|---|---|
| 4a | Keep the top 3 winners, and make everyone else "Other or tie" |
| 4b | Winner map → `.html` |
| 4c | Light-to-dark map of a number (margin, total) |

<details><summary>Hint</summary>

`gdf.explore(column=..., categorical=True, cmap=[colors], legend=True)`, then `.save(out)`
</details>

✅ Open the `.html` in your browser. Does it look like the real thing?

### Step 5: One command (`cli.py`)

| Code | Does |
|---|---|
| 5a | `my-election-map FILE --csv-only` |
| 5b | `my-election-map FILE --boundaries SHAPES` → a map |

<details><summary>Hint</summary>

`argparse.ArgumentParser()`, then `add_argument(...)` for each option, then `parse_args(argv)`
</details>

✅ This makes your own Mayor map:
```bash
my-election-map data/Poll_By_Poll_Mayor.xlsx --boundaries data/subdivisions.gpkg --out my_mayor
```

---

## Part 2: The smaller races

Same code, new files. Each one breaks something different.

### Step 6: Councillor

There's a different race in every ward, which means **69 different winners**: too many colors for a map.

- **6a.** Does your parser read `Poll_By_Poll_Councillor.xlsx`? (It might already!)
- **6b.** Add `--ward 10` to map one ward, and use `--color margin_pct` for the whole city.

✅ 932,157 votes.

### Step 7: School boards

- **7a.** In `Poll_By_Poll_TDSB.xlsx`, one school ward covers parts of several city wards, so one sheet has **several blocks**. Does your parser reset properly at each "Subdivision" row?
- **7b.** The French public board (`TFDSB`) got only 2,652 votes, so most subdivisions are **empty**. Does Step 2c hold up?

✅ TDSB: 672,546 votes.

### Step 8: All offices in one file

`Poll_By_Poll_All_Offices.xlsx` has **31 races**, 6 to a sheet.

- **8a.** Does your parser pick up each race's name from its title row?
- **8b.** Add `--list` (print the races) and `--contest Mayor` (pick one).

✅ `--contest Mayor` gives 982,660 votes, the same as the Mayor file.

---

🎉 All checks pass: `python -m pytest practice -rs`. You built the whole tool.

**Next, with no answer key:** a turnout rank column, or a 2023 vs 2026 change map.

# Build it yourself: Mayor map in 4 steps

You write 4 functions in **`practice/my_map.py`**.
You need **2 tools**: pandas (tables) and geopandas (map shapes).

**Setup (once):**
```bash
pip install -e ".[dev]"
```

**After each step:**
```bash
python -m pytest -rs -k step1
git add practice && git commit -m "step 1" && git push
```
(Change `step1` to the step you're on. `SKIPPED` means not written yet.)

---

## Step 1: All tabs into one table

| Use | For |
|---|---|
| `pd.read_excel(path, sheet_name=None, header=1)` | Read all tabs, using the "Subdivision" row as the header |
| filter rows | Drop the "Mayor" row and the "City Ward N Totals" row |
| `.melt()` | Flip it, so the subdivision columns become rows |
| new column | `ward` = the number from the tab name ("Ward 1" gives 1) |
| `pd.concat(tables, ignore_index=True)` | Stack all 25 tabs (`ignore_index` gives every row its own number) |

✅ The votes add up to **982,660**.

## Step 2: One row per subdivision

| Use | For |
|---|---|
| `groupby(["ward", "subdiv"])` | Group the rows by subdivision |
| `.sum()` | Total votes |
| `.idxmax()` or sort + `.first()` | The candidate with the most votes = the winner |

✅ 1,431 rows. Chow won 1,014 of them, and Bradford 406.

## Step 3: Attach votes to map shapes

| Use | For |
|---|---|
| `f"{ward:02d}{subdiv:03d}"` | Make a code like `01005`, the way the map layer writes it |
| `shapes.merge(summary, ...)` | Join on that code |

Real shapes: in QGIS, right-click *Voting Subdivision 2026* → **Export → Save Features As…** → GeoPackage → `data/subdivisions.gpkg`.
Then load them with `gpd.read_file("data/subdivisions.gpkg")`.

✅ 1,348 shapes matched in the check (on the real file: 1,356).

## Step 4: Draw the map

| Use | For |
|---|---|
| `gdf.explore(column="winner")` | An interactive map, colored by winner |
| `.save(out)` | Write the `.html` file |

✅ Open the `.html` in your browser.

---

**Later, once all 4 work:** ties (two candidates level), the Councillor file, the school board files.

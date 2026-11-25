# election_map

Turn Toronto poll-by-poll result spreadsheets into interactive maps, with one command.

```
election-map data/Poll_By_Poll_Mayor.xlsx --boundaries subdivisions.gpkg
```

What you get:
* `mayor.html`: an interactive map with an OpenStreetMap background, a legend, and hover details. Open it in any browser.
* `mayor.csv`: one clean row per subdivision. Use it in QGIS, Excel, or anywhere else.
* `mayor.png` (add `--png`): a static image for slides and reports.

New to Python? Read **LEARN.md** first. It walks through the code in the order the data flows.
Want to write it yourself? **BUILD_IT_YOURSELF.md** rebuilds the tool step by step in `practice/`, with checkers for every step.

## Setup (Mac, one time)

```bash
cd election_map
python3 -m venv .venv            # a private Python just for this project
source .venv/bin/activate        # run this each time you open a new terminal
pip install -e ".[dev]"          # installs the tool plus pytest and jupyter
```

Put the `Poll_By_Poll_*.xlsx` files in `data/`.

## Get the boundaries (the one manual step)

Pick **one** of these:

1. **From QGIS (most reliable).** Right-click your *Voting Subdivision 2026* layer, then **Export → Save Features As…** Set Format to **GeoPackage** and the file name to `data/subdivisions.gpkg`.
2. **Straight from the city.** Use `--boundaries https://gis.toronto.ca/arcgis/rest/services/cot_geospatial6/FeatureServer/10` (layer 10 is "the most current election"). If that fails, use option 1.

The tool works out which boundary column matches ward + subdivision by itself, and prints what it chose:

```
Join: AREA_LONG_CODE as WWSSS (01005), 1348/1348 shapes matched
```

If it prints a WARNING or picks an odd column, see *Troubleshooting*.

## Recipes

```bash
# Who won each subdivision
election-map data/Poll_By_Poll_Mayor.xlsx --boundaries data/subdivisions.gpkg

# Two-way swing map: blue = Chow ahead, red = Bradford ahead, gray = even
election-map data/Poll_By_Poll_Mayor.xlsx --boundaries data/subdivisions.gpkg \
    --compare "Chow Olivia" "Bradford Brad" --color a_minus_b --png

# Councillor races: how close each subdivision was, citywide
election-map data/Poll_By_Poll_Councillor.xlsx --boundaries data/subdivisions.gpkg --color margin_pct

# One ward's councillor race: who won each subdivision
election-map data/Poll_By_Poll_Councillor.xlsx --boundaries data/subdivisions.gpkg --ward 10

# Files with several races in them
election-map data/Poll_By_Poll_All_Offices.xlsx --list
election-map data/Poll_By_Poll_All_Offices.xlsx --contest Mayor --boundaries data/subdivisions.gpkg

# Just the clean table
election-map data/Poll_By_Poll_TDSB.xlsx --csv-only
```

`--color` options:

| Option | What it shows | Colors |
|---|---|---|
| `winner` (default) | Who came first | The 3 biggest winners get their own color; everyone else is "Other or tie" |
| `margin_pct` | How close it was (1st % minus 2nd %) | Light = close, dark = landslide |
| `winner_pct` | Winner's share of the vote | Light to dark |
| `total` | Votes cast (turnout) | Light to dark |
| `a_minus_b` | Head-to-head, needs `--compare A B` | Blue for A, red for B, gray for even |

`election-map --help` lists every option.

## Checks built into the tool

* **Every block of every sheet is checked against the official "City Ward N Totals" row.** If a single number disagrees, the tool stops with the ward and subdivision.
* Ties are labelled "Tie" instead of being handed to whoever is listed first.
* The join report shows how many shapes matched, and lists results with no shape. Subdivisions 90 and above are advance, mail, and institutional polls, which have no area on the map.

Run the tests any time you change the code: `python -m pytest -q`

## Troubleshooting

| You see | Do this |
|---|---|
| `WARNING: under 80% of shapes matched` | The boundaries are probably from a different election than the results. |
| The join used a weird column | Name it yourself: `--key-field AREA_LONG_CODE` |
| `Couldn't match any boundary field` | Open the boundary file in Python (`gpd.read_file(...).head()`) to see how its codes are written, then add that format to `KEY_FORMATS` in `geo.py` (one line). |
| `ParseError: ... we counted X but the sheet says Y` | The spreadsheet layout changed. Look at that sheet; `parse.py` explains the rules it follows. |
| The map is blank in the browser | The map's code and background tiles load from the internet. Check your connection. |

## Data notes

* From the city's Readme: ward 21 subdivisions 11 and 14 were already corrected in these files. Their tabulators were swapped on election night, so use these files, not election-night numbers.
* Subdivisions 98 and 99 are advance-vote locations.

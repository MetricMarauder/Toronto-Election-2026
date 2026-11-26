# election_map: notes for Claude Code

## Who this is for
The owner is **learning Python** through this project and said: "teach me, don't do it all for me." When they ask for a change:
- Explain the idea first, point to the file and function, and let them try it.
- Write the code only when they ask, or after they've had a go. Keep changes small and explain each line that matters.
- Use plain language, and use visual or step-by-step explanations where you can.

## practice/ is the owner's own code
`practice/my_election_map/` is a step-by-step rebuild the owner writes themselves, following BUILD_IT_YOURSELF.md. Its functions start empty on purpose.
- Never fill them in unprompted. Give hints in the guide's style, one at a time. Point to the matching function on the `main` branch only if they're stuck.
- On this branch the owner removed all AI-written code: `election_map/`, `tests/` and `notebooks/` exist only on `main`. Don't add them back here.
- Checkers: `python -m pytest practice -rs -k 1a` (steps not yet written show as SKIPPED). They compare with saved answers in `practice/answers/`.

## What it does
Toronto poll-by-poll .xlsx files → one row per subdivision → join to voting-subdivision polygons → folium map (HTML) plus optional PNG.
Pipeline: `parse.py` → `metrics.py` → `geo.py` → `mapmaker.py`, wired together in `__main__.py` (`election-map` CLI).

## Facts already established (don't re-derive)
- Workbook layout: one sheet per ward. Blocks start at a "Subdivision" row and end at "City Ward N Totals". School-board sheets have several city-ward blocks; All_Offices has 6 races per sheet. The parser checks every block against its Totals row.
- Mayor total: 982,660 votes across 1,431 subdivision rows. Chow 1,014 / Bradford 406 / 11 ties.
- Subdivisions 90+ are advance, mail, or institutional polls and have no polygon. 98 and 99 are advance vote.
- Ward 21 subdivisions 11 and 14 were already corrected in these files (see data/Readme.txt).
- Boundaries: City of Toronto ArcGIS `cot_geospatial6/FeatureServer/10` ("Voting Subdivision", most current election). Fields include AREA_SHORT_CODE, AREA_LONG_CODE, AREA_NAME. **The real key format has not been confirmed yet.** The code auto-detects it (`geo.detect_key`) and prints its choice; check that on the first real run. The owner also has the layer in QGIS as "Voting Subdivision 2026".
- Map colors: at most 3 category colors on a choropleth (the rest go to "Other or tie"); diverging red–gray–blue on a symmetric scale; sequential single-hue blue.

## Commands
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
- Tests: `python -m pytest -q` (they use fake square boundaries, so they work offline)
- Example: `election-map data/Poll_By_Poll_Mayor.xlsx --boundaries data/subdivisions.gpkg --png`

## Next steps the owner may want
1. First real run with the boundaries exported from QGIS: confirm the join report shows about 1,348 shapes matched.
2. LEARN.md exercises 4 (turnout_rank) and 7 (turnout per voter).
3. A 2022/2023 vs 2026 comparison map.

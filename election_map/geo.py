"""
STEP 3 — Get the boundary shapes and join the votes onto them.

Two problems this module solves for you:

1. Loading boundaries from anywhere.
   - a file:        subdivisions.gpkg / .shp / .geojson (export from QGIS works)
   - an ArcGIS URL: .../FeatureServer/10  (the City of Toronto's servers)
   ArcGIS servers hand out at most ~2000 shapes per request, so we "page":
   ask for 0-1999, then 2000-3999, ... until a page comes back short.

2. Finding the join key without guessing.
   The results only know (ward=1, subdiv=5). The boundary layer has some
   text field that encodes the same thing — maybe "01005", "1005", "1-5".
   Instead of you squinting at attribute tables (what we did in QGIS),
   detect_key() tries every format against every text column and keeps
   the combination that matches the most rows.
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd

# Ways a (ward, subdivision) pair might be written as text. Add more here
# if a future boundary file uses a format we haven't seen.
KEY_FORMATS = {
    "WWSSS (01005)": lambda w, s: f"{w:02d}{s:03d}",
    "WSSS (1005)":   lambda w, s: f"{w}{s:03d}",
    "W-S (1-5)":     lambda w, s: f"{w}-{s}",
    "WW-SSS (01-005)": lambda w, s: f"{w:02d}-{s:03d}",
    "WWSS (0105)":   lambda w, s: f"{w:02d}{s:02d}",
}


def as_text(column: pd.Series) -> pd.Series:
    """Make any column comparable as text. 1005.0 (a float) becomes "1005"."""
    def one(v):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v).strip()
    return column.map(one)


def load_boundaries(source: str, page_size: int = 2000) -> gpd.GeoDataFrame:
    """Load polygons from a file path or an ArcGIS FeatureServer layer URL."""
    if str(source).startswith("http"):
        frames, offset = [], 0
        while True:
            url = (f"{source.rstrip('/')}/query?where=1%3D1&outFields=*&f=geojson"
                   f"&resultOffset={offset}&resultRecordCount={page_size}")
            page = gpd.read_file(url)
            frames.append(page)
            if len(page) < page_size:
                break
            offset += page_size
        gdf = pd.concat(frames, ignore_index=True)
        gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=frames[0].crs)
    else:
        if not Path(source).exists():
            raise FileNotFoundError(source)
        gdf = gpd.read_file(source)
    return gdf.to_crs(4326)       # web maps want plain latitude/longitude


def detect_key(boundaries: gpd.GeoDataFrame, summary: pd.DataFrame, field: str = None):
    """Return (boundary_field, format_name, match_rate) with the best match.

    match_rate = share of polygons that found a result row.
    """
    pairs = summary[["ward", "subdiv"]].drop_duplicates()
    candidates = [field] if field else [c for c in boundaries.columns if c != "geometry"]
    best, best_score = (None, None, 0.0), (0.0, False)
    for col in candidates:
        values = set(as_text(boundaries[col]))
        is_text = not pd.api.types.is_numeric_dtype(boundaries[col])
        for name, fmt in KEY_FORMATS.items():
            keys = {fmt(w, s) for w, s in pairs.itertuples(index=False)}
            rate = len(values & keys) / max(len(values), 1)
            # On a tie, prefer text columns: codes like "01005" are stored as text,
            # while plain counters (OBJECTID 1, 2, 3...) can match by coincidence.
            if (rate, is_text) > best_score:
                best, best_score = (col, name, rate), (rate, is_text)
    return best


def join(boundaries, summary, field=None, key_format=None, detect_with=None):
    """Attach summary rows to polygons. Returns (GeoDataFrame, report dict).

    detect_with: a fuller table (all wards) to detect the key format from.
    Detecting on one ward alone is unreliable — fewer rows, more coincidences.
    """
    if key_format is None:
        field, key_format, rate = detect_key(
            boundaries, summary if detect_with is None else detect_with, field)
        if field is None or rate == 0:
            raise ValueError(
                "Couldn't match any boundary field to ward+subdivision. Look at "
                "boundaries.head() and add the format to KEY_FORMATS in geo.py."
            )
    fmt = KEY_FORMATS[key_format]
    summary = summary.copy()
    summary["key"] = [fmt(w, s) for w, s in zip(summary["ward"], summary["subdiv"])]

    left = boundaries.assign(key=as_text(boundaries[field]))
    merged = left.merge(summary, on="key", how="outer", indicator=True)

    report = {
        "boundary_field": field,
        "key_format": key_format,
        "matched": int((merged["_merge"] == "both").sum()),
        "shapes_without_results": int((merged["_merge"] == "left_only").sum()),
        "results_without_shapes": int((merged["_merge"] == "right_only").sum()),
        # Usually advance/mail/institution polls (subdivisions 90+): no area to draw.
        "unmapped_examples": merged.loc[merged["_merge"] == "right_only", "key"].head(8).tolist(),
    }
    mapped = merged[merged["_merge"] != "right_only"].drop(columns="_merge")
    return gpd.GeoDataFrame(mapped, geometry="geometry", crs=boundaries.crs), report

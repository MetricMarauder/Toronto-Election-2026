"""
Make FAKE subdivision shapes for testing: a grid of squares over Toronto,
one per subdivision, named like the real layer (AREA_LONG_CODE = "01005").

Why fake data? Tests should run anywhere, offline, in a second. They prove
the plumbing works; they can't prove the real key format, so the real
boundary file still gets checked by the join report.
"""
import geopandas as gpd
from shapely.geometry import box


def fake_boundaries(summary, key="AREA_LONG_CODE", fmt=lambda w, s: f"{w:02d}{s:03d}"):
    pairs = summary[["ward", "subdiv"]].drop_duplicates()
    pairs = pairs[pairs.subdiv < 90]                 # advance polls have no area
    rows = []
    for i, (w, s) in enumerate(pairs.itertuples(index=False)):
        col, row = (w - 1) % 5, (w - 1) // 5         # 5x5 grid of wards
        x0 = -79.60 + col * 0.06 + (s % 8) * 0.0075
        y0 = 43.60 + row * 0.04 + ((s // 8) % 8) * 0.005
        rows.append({"OBJECTID": i + 1, key: fmt(w, s), "geometry": box(x0, y0, x0 + 0.0075, y0 + 0.005)})
    return gpd.GeoDataFrame(rows, crs=4326)

"""
STEP 3: Load the subdivision shapes and attach the votes to them.

The results know a subdivision as two numbers: ward=1, subdiv=5.
The city's boundary layer knows it as ONE text code in the column
AREA_LONG_CODE: "01005" (2-digit ward, then 3-digit subdivision).
(We confirmed this format on the first real run: 1,356 of 1,356 shapes matched.)

So the whole join comes down to: build the same code on the results side,
then merge on it.
"""
import geopandas as gpd
import pandas as pd


# ---------------------------------------------------------------- Step 3a
def make_key(ward: int, subdiv: int) -> str:
    """Write a (ward, subdivision) pair the way the boundary layer does.

        make_key(1, 5)    -> "01005"
        make_key(25, 112) -> "25112"
    """
    raise NotImplementedError("Step 3a: make_key")


# ---------------------------------------------------------------- Step 3b
def load_boundaries(source) -> gpd.GeoDataFrame:
    """Load polygons from a file (.gpkg, .shp, .geojson) and return them
    in latitude/longitude (EPSG:4326), which web maps expect.

    If the file doesn't exist, raise FileNotFoundError.
    """
    raise NotImplementedError("Step 3b: load_boundaries")


# ---------------------------------------------------------------- Step 3c
def join(shapes: gpd.GeoDataFrame, summary: pd.DataFrame, field: str = "AREA_LONG_CODE"):
    """Attach summary rows to shapes. Return (GeoDataFrame, report).

    The GeoDataFrame: one row per SHAPE, with the summary columns added
    (shapes with no results keep empty values in those columns).

    The report is a dict that says how well the join went:
        {"matched": ...,                  shapes that found a result row
         "shapes_without_results": ...,   shapes nobody voted in (should be ~0)
         "results_without_shapes": ...}   results with no area: advance/mail polls (90+)
    """
    raise NotImplementedError("Step 3c: join")

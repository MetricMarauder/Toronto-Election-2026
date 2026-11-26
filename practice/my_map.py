"""
Your code. Four steps, one function each.
For each one: delete the `raise NotImplementedError` line and write your own.

Guide: BUILD_IT_YOURSELF.md
"""
import pandas as pd
import geopandas as gpd


def step1_read_all_tabs(path):
    """All 25 tabs -> one table.

    Return columns: ward, subdiv, candidate, votes
    (one row per candidate per subdivision)
    """
    raise NotImplementedError("step 1")


def step2_summarize(long):
    """One row per subdivision.

    Return columns: ward, subdiv, total, winner
    """
    raise NotImplementedError("step 2")


def step3_join(shapes, summary):
    """Attach the summary to the map shapes.

    shapes has a column AREA_LONG_CODE like "01005" (ward 1, subdivision 5).
    Return the shapes with the summary columns added.
    """
    raise NotImplementedError("step 3")


def step4_map(gdf, out="map.html"):
    """Color each subdivision by its winner and save to `out`."""
    raise NotImplementedError("step 4")

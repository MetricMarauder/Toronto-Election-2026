"""
STEP 4: Draw the map.

A GeoDataFrame can draw itself as an interactive web map:
    gdf.explore(column="winner")       -> a folium Map
    m.save("map.html")                 -> a file anyone can open in a browser

Most of the work is choosing COLORS well:
  * WHO won (categories)  -> distinct hues, but only 3. Touching shapes in 4+
    hues are hard to tell apart, especially for colorblind readers.
  * HOW MUCH (amounts)    -> one hue, light to dark.
"""
import pandas as pd

CATEGORY_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]   # blue, orange, aqua
OTHER_COLOR = "#b4b2a9"                               # gray for "Other or tie"


# ---------------------------------------------------------------- Step 4a
def winner_groups(winners: pd.Series) -> pd.Series:
    """Fold small winners into "Other or tie" so the map needs only 4 colors.

    Keep the 3 candidates who won the MOST subdivisions ("Tie" doesn't count
    as a candidate). Everyone else, and every "Tie", becomes "Other or tie".
    Missing values (no votes) stay missing.

        in:  ["Chow", "Chow", "Chow", "Bradford", "Bradford", "Saunders", "Saunders",
              "Matlow", "Tie", None]
        out: ["Chow", "Chow", "Chow", "Bradford", "Bradford", "Saunders", "Saunders",
              "Other or tie", "Other or tie", None]

    (Chow won 3, Bradford 2, Saunders 2: those are the top 3. Matlow won 1,
    so Matlow folds into "Other or tie".)
    """
    raise NotImplementedError("Step 4a: winner_groups")


# ---------------------------------------------------------------- Steps 4b + 4c
def make_map(gdf, out: str = "map.html", color: str = "winner"):
    """Save an interactive map to `out` and return the folium Map.

    Step 4b. color="winner": color each shape by winner_groups(gdf["winner"]),
             using CATEGORY_COLORS for the top 3 and OTHER_COLOR for the rest.
             Show a legend, and a tooltip with ward, subdiv, total, winner,
             winner_pct.

    Step 4c. Any other color (like "margin_pct" or "total"): a light-to-dark
             map of that number, with a legend.
    """
    raise NotImplementedError("Step 4b: make_map")

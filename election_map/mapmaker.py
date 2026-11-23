"""
STEP 4 — Draw the interactive map.

GeoDataFrame.explore() builds a Leaflet web map (via the folium library):
an OpenStreetMap basemap, your polygons on top, a legend, and a hover
tooltip. The output is a single .html file anyone can open in a browser.

Color choices follow a few rules worth learning:
  * WHO won (categories)   -> distinct hues, but only 3 on a filled map.
    More than 3 hues on touching shapes become hard to tell apart,
    especially for colorblind readers, so the rest fold into "Other".
  * HOW MUCH (one-sided)   -> one hue, light to dark ("sequential").
  * WHICH WAY (two-sided)  -> two hues with neutral gray at zero ("diverging").
    The scale must be symmetric (-50..+50) so gray really means "even".
"""
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap

CATEGORY_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]   # blue, orange, aqua
OTHER_COLOR = "#b4b2a9"                               # neutral gray
NO_DATA_COLOR = "#f0efec"

SEQUENTIAL = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
DIVERGING = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])

# Register the ramps by name. explore() handles a named colormap more reliably
# than a colormap object (an object + empty polygons hits a geopandas bug).
for _cmap, _name in ((SEQUENTIAL, "election_seq"), (DIVERGING, "election_div")):
    if _name not in colormaps:
        colormaps.register(_cmap, name=_name)

TOOLTIP = ["ward", "subdiv", "contest", "total", "winner", "winner_pct", "runner_up", "margin_pct"]


def winner_groups(gdf):
    """Add a 'Winner' column: top 3 candidates by subdivisions won, else 'Other or tie'."""
    wins = gdf["winner"][gdf["winner"].ne("Tie")].value_counts()
    top = wins.index[:3].tolist()
    gdf = gdf.copy()
    gdf["Winner"] = gdf["winner"].where(gdf["winner"].isin(top), "Other or tie")
    gdf.loc[gdf["winner"].isna(), "Winner"] = None
    cats = top + (["Other or tie"] if (gdf["Winner"] == "Other or tie").any() else [])
    colors = CATEGORY_COLORS[: len(top)] + ([OTHER_COLOR] if len(cats) > len(top) else [])
    return gdf, cats, colors


def static_map(gdf, color="winner", out="map.png", title=None, compare=None):
    """Same colours as make_map, as a PNG for reports and slides (no basemap)."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(figsize=(11, 8))
    edge = dict(edgecolor="#52514e", linewidth=0.15)
    gdf[gdf.geometry.notna()].plot(ax=ax, color=NO_DATA_COLOR, **edge)
    if color == "winner":
        g, cats, colors = winner_groups(gdf)
        for cat, col in zip(cats, colors):
            g[g["Winner"] == cat].plot(ax=ax, color=col, **edge)
        ax.legend(handles=[Patch(color=c, label=k) for k, c in zip(cats, colors)],
                  loc="lower right", frameon=False)
    else:
        vals = gdf[color].astype(float)
        if color == "a_minus_b":
            limit = max(10, round(float(vals.abs().quantile(0.98)) / 10) * 10)
            kw = dict(cmap=DIVERGING, vmin=-limit, vmax=limit)
            label = f"{compare[0]} % minus {compare[1]} %" if compare else color
        else:
            kw = dict(cmap=SEQUENTIAL)
            label = color
        gdf.assign(_v=vals).plot(ax=ax, column="_v", legend=True, **kw, **edge,
                                 legend_kwds={"label": label, "shrink": 0.6})
    ax.set_axis_off()
    if title:
        ax.set_title(title, loc="left", fontsize=15)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def make_map(gdf, color="winner", out="map.html", title=None, compare=None):
    """Save an interactive map coloured by `color` and return the folium Map."""
    gdf = gdf.copy()
    tooltip = [c for c in TOOLTIP + ["a_pct", "b_pct", "a_minus_b"] if c in gdf.columns]
    common = dict(tooltip=tooltip, tiles="OpenStreetMap",
                  style_kwds={"weight": 0.4, "color": "#52514e", "fillOpacity": 0.65},
                  missing_kwds={"color": NO_DATA_COLOR, "label": "No results"})

    if color == "winner":
        gdf, cats, colors = winner_groups(gdf)
        m = gdf.explore(column="Winner", categorical=True, categories=cats,
                        cmap=colors, legend=True, **common)

    elif color == "a_minus_b":
        if compare is None or "a_minus_b" not in gdf.columns:
            raise ValueError("Use --compare 'Name A' 'Name B' to map a_minus_b")
        limit = max(10, float(gdf["a_minus_b"].abs().quantile(0.98)))
        limit = round(limit / 10) * 10 or 10            # tidy number like 50
        m = gdf.explore(column="a_minus_b", cmap="election_div", vmin=-limit, vmax=limit,
                        legend=True, legend_kwds={"caption": f"{compare[0]} % minus {compare[1]} %"},
                        **common)

    else:
        gdf[color] = gdf[color].astype(float)
        m = gdf.explore(column=color, cmap="election_seq", legend=True,
                        vmin=float(gdf[color].min()), vmax=float(gdf[color].max()),
                        legend_kwds={"caption": color}, **common)

    if title:
        import folium
        m.get_root().html.add_child(folium.Element(
            f'<div style="position:fixed;top:10px;left:60px;z-index:999;background:white;'
            f'padding:6px 12px;border-radius:6px;font:500 15px system-ui,sans-serif;'
            f'box-shadow:0 1px 4px rgba(0,0,0,.2)">{title}</div>'))
    m.save(out)
    return m

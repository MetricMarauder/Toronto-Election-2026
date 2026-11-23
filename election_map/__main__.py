"""
STEP 5 — One command for the whole pipeline.

    python -m election_map RESULTS.xlsx --boundaries SHAPES [options]

Examples
    # who won each subdivision, mayor
    python -m election_map Poll_By_Poll_Mayor.xlsx --boundaries subdivisions.gpkg

    # two-way swing map
    python -m election_map Poll_By_Poll_Mayor.xlsx --boundaries subdivisions.gpkg \
        --compare "Chow Olivia" "Bradford Brad" --color a_minus_b

    # councillor: closeness of each race
    python -m election_map Poll_By_Poll_Councillor.xlsx --boundaries subdivisions.gpkg \
        --color margin_pct

    # just the clean table, no map (handy for QGIS or Excel)
    python -m election_map Poll_By_Poll_TDSB.xlsx --csv-only

argparse turns the options below into a --help page for free:
    python -m election_map --help
"""
import argparse
import sys
from pathlib import Path

from .parse import read_poll_by_poll
from .metrics import summarize, check_against_sheet


def main(argv=None):
    p = argparse.ArgumentParser(prog="election_map", description="Poll-by-poll results to a map")
    p.add_argument("results", help="poll-by-poll .xlsx file")
    p.add_argument("--boundaries", help="boundary file (.gpkg/.shp/.geojson) or ArcGIS layer URL")
    p.add_argument("--contest", help="pick one contest when a file has several (see --list)")
    p.add_argument("--ward", type=int, nargs="+", help="only these city wards, e.g. --ward 10 11")
    p.add_argument("--list", action="store_true", help="list contests in the file and stop")
    p.add_argument("--compare", nargs=2, metavar=("A", "B"), help="two candidates for a swing map")
    p.add_argument("--color", default="winner",
                   help="winner | margin_pct | winner_pct | total | a_minus_b (default winner)")
    p.add_argument("--key-field", help="boundary column holding ward+subdivision (auto if omitted)")
    p.add_argument("--out", help="output name without extension (default: from the results file)")
    p.add_argument("--png", action="store_true", help="also save a static .png image")
    p.add_argument("--csv-only", action="store_true", help="write the summary CSV and stop")
    args = p.parse_args(argv)

    long = read_poll_by_poll(args.results)          # raises if totals don't match
    contests = long["contest"].unique().tolist()
    if args.list:
        print("\n".join(contests))
        return 0
    if args.contest is None and len(contests) > 1 and "All_Offices" in args.results:
        sys.exit("This file has several races. Pick one with --contest (see --list).")

    all_pairs = long[["ward", "subdiv"]].drop_duplicates()     # for key detection later
    if args.ward:
        long = long[long["ward"].isin(args.ward)]
    summary = summarize(long, compare=args.compare, contest=args.contest)
    if args.color == "winner" and summary["winner"].nunique() > 4:
        print(f"Note: {summary['winner'].nunique()} different winners; a map can only show 3 "
              "distinct colours, so the rest become 'Other'. For separate races (councillor, "
              "trustee) try --color margin_pct, or zoom in with --ward N.")
    check_against_sheet(long if args.contest is None else long[long.contest == args.contest], summary)

    out = Path(args.out or Path(args.results).stem.replace("Poll_By_Poll_", "").lower())
    summary.to_csv(out.with_suffix(".csv"), index=False)
    print(f"Parsed {len(long):,} vote rows -> {len(summary):,} subdivisions "
          f"({summary['total'].sum():,} votes). Wrote {out.with_suffix('.csv')}")
    if args.csv_only:
        return 0
    if not args.boundaries:
        sys.exit("Add --boundaries to draw a map (or --csv-only for just the table).")

    from .geo import load_boundaries, join          # heavy imports only when mapping
    from .mapmaker import make_map

    shapes = load_boundaries(args.boundaries)
    gdf, report = join(shapes, summary, field=args.key_field, detect_with=all_pairs)
    if args.ward:                                   # zoomed in: drop other wards' shapes
        gdf = gdf[gdf["total"].notna()]
        report["shapes_without_results"] = 0
    total = report["matched"] + report["shapes_without_results"]
    print(f"Join: {report['boundary_field']} as {report['key_format']}, "
          f"{report['matched']}/{total} shapes matched")
    if report["results_without_shapes"]:
        print(f"  {report['results_without_shapes']} result rows had no shape "
              f"(usually advance/mail polls), e.g. {report['unmapped_examples']}")
    if report["matched"] < 0.8 * total:
        print("  WARNING: under 80% of shapes matched. Are the boundaries from the same election?")

    title = args.contest or (contests[0] if len(contests) == 1 else out.name)
    make_map(gdf, color=args.color, out=str(out.with_suffix(".html")), title=title, compare=args.compare)
    print(f"Map saved to {out.with_suffix('.html')}")
    if args.png:
        from .mapmaker import static_map
        static_map(gdf, color=args.color, out=str(out.with_suffix(".png")), title=title, compare=args.compare)
        print(f"Image saved to {out.with_suffix('.png')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
STEP 5: One command that runs the whole pipeline.

When you're done, this works from any folder:

    my-election-map data/Poll_By_Poll_Mayor.xlsx --csv-only
    my-election-map data/Poll_By_Poll_Mayor.xlsx --boundaries data/subdivisions.gpkg
    my-election-map --help

(The `my-election-map` command is wired up in pyproject.toml. After
`pip install -e .` it calls the main() function below.)

Use YOUR functions from the other steps:
    from my_election_map.parse import read_poll_by_poll
    ... and so on.
"""
import argparse
import sys


# ---------------------------------------------------------------- Steps 5a + 5b
def main(argv=None) -> int:
    """Run the pipeline. `argv` is the list of command-line words (None = the real ones).

    Step 5a. Options:
        results         the .xlsx file (required, no dashes)
        --out NAME      output name without extension (default: "map")
        --csv-only      write NAME.csv and stop
        --boundaries F  boundary file to draw the map with
        --color C       winner | margin_pct | winner_pct | total  (default winner)
    Parse the file, summarize it, write NAME.csv, and print one line like:
        Parsed 75,843 vote rows -> 1,431 subdivisions (982,660 votes)

    Step 5b. Unless --csv-only: load the boundaries, join, print the join
    report, and save NAME.html with make_map. If --boundaries is missing,
    stop with a helpful message.

    Return 0 when everything worked.
    """
    raise NotImplementedError("Step 5a: main")


if __name__ == "__main__":
    sys.exit(main())

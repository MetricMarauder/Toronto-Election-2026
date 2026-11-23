"""election_map: turn poll-by-poll election spreadsheets into maps."""
from .parse import read_poll_by_poll
from .metrics import summarize

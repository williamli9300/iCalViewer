# iCalViewer

#### by Will Li | [https://github.com/williamli9300/iCalViewer/](https://github.com/williamli9300/iCalViewer/) | v0.1.0

A simple Python utility to print out all events in an iCalendar file.
The following options (type, **default**) can be changed under the `main()` function:
- `earliest_date` (int (yyyymmdd), **0**): earliest start date for an event to be included.
- `write_file_` (bool, **True**): export text file?
- `print_outp` (bool, **True**): print to console?
- `alt_location` (str, "**TBD**"): Text for location field to include if no location is provided.
- `include_repeats` (bool, **True**): Include repeat information for repeating events.
- `include_description` (bool, **True**): Include event descriptions if applicable.


## How To Use
1. Place your `icalviewer.py` in the same directory as your `*.ics` file of interest.
2. Open `icalviewer.py` to adjust your desired parameters, then run the file using a console or IDE.

## Compatibility and Dependencies.
- Requires Python 3.x. Uses the standard `datetime` and `os` libraries.
- Designed to work with iCalendar Version 2.0 files.

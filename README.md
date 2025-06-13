# melissa-donnie

This project reads an Excel file and sends each row as a `Checked In` event to Segment.

## Usage

1. Install dependencies:

```bash
pip install pandas requests openpyxl
```

2. Prepare an Excel file (e.g., `data.xlsx`) with the following columns:

- `email`
- `phone`
- `club_name`
- `club_location`
- `membership_level`
- `timestamp` (parseable date/time)

3. Set your Segment write key in the `SEGMENT_WRITE_KEY` environment variable or edit `segment_excel.py` to include it.

4. Run the script:

```bash
python segment_excel.py data.xlsx
```

The script hashes the email to create the user identifier, cleans phone numbers and email addresses, and sends the remaining fields as properties. Each row's timestamp is used as the event timestamp in ISO 8601 format.

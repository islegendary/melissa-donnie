# melissa-donnie

This project processes an Excel file, extracts columns, and submits track calls to the Segment.io endpoint.

## Usage

1. Install dependencies:

```bash
pip install pandas requests openpyxl
```

2. Prepare an Excel file (e.g., `data.xlsx`) with at least two columns:

   - `userId` – the unique identifier for the user. If you don't have a user ID,
     include an `email` column instead and the script will use it as the
     identifier.

   - `event` – the event name to track.
   - Any additional columns will be included as properties in the Segment track payload.

3. Set your Segment write key in the `SEGMENT_WRITE_KEY` environment variable or pass it with `--write-key`.

4. Run the script:

```bash
python segment_excel.py data.xlsx
```
You can customize column names with `--user-id-col`, `--event-col`, `--email-col`,
and `--phone-col` if they differ from the defaults. If the specified user ID
column is missing, the script falls back to the email column.
Identifiers can be hashed with `--hash-id`, and phone numbers with
`--hash-phone`. Use `--batch-size` to control how many events are sent in a
single request.

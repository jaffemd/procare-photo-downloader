# Procare Photo Downloader

A local web app for downloading photos from Procare by date range.

## Setup

```bash
pip install flask requests
python3 app.py
```

Then open [http://localhost:8080](http://localhost:8080).

## Usage

1. **Get your bearer token** — log in to [schools.procareconnect.com/dashboard](https://schools.procareconnect.com/dashboard), open DevTools → Network tab, find a `daily_activities` request, and copy the `Authorization` header value.
2. **Paste the token** into the app. It's saved in your browser's localStorage for next time.
3. **Pick a date range** and click **Download Photos**.

Photos are saved to `photos/YYYY-MM-DD_HHMMSS/` — a new folder per run.

## Notes

- The bearer token expires periodically. If you get an "Unauthorized" error, grab a fresh one from DevTools.
- The app must stay running while downloading. For large date ranges this can take a minute.
- The `kid_id` is hardcoded in `app.py` for Micah. To use with a different child, update the `KID_ID` constant.

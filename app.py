import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

KID_ID = "80773bb5-e422-48d1-acbf-430be8dd4cd8"
PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "photos")


def fetch_page(session, token, date_to, page):
    url = (
        f"https://api-school.procareconnect.com/api/web/parent/daily_activities/"
        f"?kid_id={KID_ID}"
        f"&filters%5Bdaily_activity%5D%5Bdate_to%5D={date_to}"
        f"&filters%5Bdaily_activity%5D%5Bactivity_type%5D=photo_activity"
        f"&page={page}"
    )
    response = session.get(url, headers={"Authorization": token, "Accept": "application/json"})
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/photos/<path:filename>")
def serve_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)


@app.route("/api/fetch", methods=["POST"])
def fetch_photos():
    data = request.get_json()
    token = (data.get("token") or "").strip()
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not token:
        return jsonify({"error": "Bearer token is required."}), 400
    if start_date > end_date:
        return jsonify({"error": "Start date must be before or equal to end date."}), 400

    run_folder_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_folder = os.path.join(PHOTOS_DIR, run_folder_name)
    os.makedirs(run_folder, exist_ok=True)

    session = requests.Session()
    saved_files = []
    page = 1

    while True:
        resp = fetch_page(session, token, end_date, page)

        if resp.status_code == 401:
            return jsonify({"error": "Unauthorized — check your bearer token."}), 401
        resp.raise_for_status()

        activities = resp.json().get("daily_activities", [])
        if not activities:
            break

        done = False
        for activity in activities:
            activity_date = activity.get("activity_date", "")

            if activity_date < start_date:
                done = True
                break

            activiable = activity.get("activiable") or {}
            photo_url = activiable.get("main_url")
            if not photo_url:
                continue

            filename = f"{activity_date}_{activity['id']}.jpg"
            filepath = os.path.join(run_folder, filename)

            photo_resp = session.get(photo_url)
            photo_resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(photo_resp.content)
            saved_files.append(filename)

        if done:
            break

        per_page = resp.json().get("per_page", 30)
        if len(activities) < per_page:
            break

        page += 1

    return jsonify({"folder": run_folder_name, "files": saved_files})


if __name__ == "__main__":
    app.run(debug=True, port=8080)

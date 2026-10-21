from flask import Flask, request, send_file
import requests
from datetime import date

app = Flask(__name__)

# Initial representative location for Kgalagadi
DISTRICTS = {
    "Kgalagadi": {
        "latitude": -26.02,
        "longitude": 22.40,
        "location": "Tsabong, Kgalagadi"
    }
}


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/analyse", methods=["POST"])
def analyse():
    district = request.form.get("district", "")
    start = request.form.get("start", "")
    end = request.form.get("end", "")

    if district not in DISTRICTS:
        return {"error": "Please select a supported district."}, 400

    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        return {"error": "Please enter valid dates."}, 400

    if start_date >= end_date or end_date >= date.today():
        return {"error": "Choose a valid historical date range."}, 400

    place = DISTRICTS[district]

    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_mean,precipitation_sum",
        "timezone": "Africa/Gaborone"
    }

    try:
        response = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params=params,
            timeout=30
        )

        response.raise_for_status()

        daily = response.json().get("daily", {})

        temperatures = daily.get("temperature_2m_mean", [])
        rainfall = daily.get("precipitation_sum", [])

        temperatures = [t for t in temperatures if t is not None]
        rainfall = [r for r in rainfall if r is not None]

        if not temperatures or not rainfall:
            raise ValueError("No climate data returned")

        average_temp = round(sum(temperatures) / len(temperatures), 1)
        total_rainfall = round(sum(rainfall), 1)

        return {
            "district": district,
            "location": place["location"],
            "start": start,
            "end": end,
            "average_temperature": average_temp,
            "total_rainfall": total_rainfall
        }

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

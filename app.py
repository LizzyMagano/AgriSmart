
from flask import Flask, render_template, request
import requests
from datetime import date

app = Flask(__name__)

# Initial representative location for Kgalagadi.
# These coordinates represent Tsabong, not every farm
# across the whole district.
DISTRICTS = {
    "Kgalagadi": {
        "latitude": -26.02,
        "longitude": 22.40,
        "location": "Tsabong, Kgalagadi"
    }
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyse", methods=["POST"])
def analyse():
    district = request.form.get("district", "")
    start = request.form.get("start", "")
    end = request.form.get("end", "")

    if district not in DISTRICTS:
        return render_template(
            "index.html",
            error="Please select a supported district."
        )

    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        return render_template(
            "index.html",
            error="Please enter valid dates."
        )

    if start_date >= end_date or end_date >= date.today():
        return render_template(
            "index.html",
            error="Choose a valid historical date range."
        )

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

        temperatures = daily.get("temperature_2m_mean") or []
        rainfall = daily.get("precipitation_sum") or []

        temperatures = [
            value for value in temperatures
            if value is not None
        ]
        rainfall = [
            value for value in rainfall
            if value is not None
        ]

        if not temperatures or not rainfall:
            raise ValueError("No climate data was returned.")

        average_temp = sum(temperatures) / len(temperatures)
        total_rainfall = sum(rainfall)

        # These are climate statistics, not a crop prediction yet.
        return render_template(
            "index.html",
            district=district,
            location=place["location"],
            start=start,
            end=end,
            average_temp=round(average_temp, 1),
            total_rainfall=round(total_rainfall, 1)
        )

    except (requests.RequestException, ValueError):
        return render_template(
            "index.html",
            error="Could not retrieve climate data. Please try again."
        )


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

DISTRICTS = {
    "Kgalagadi": {
        "latitude": -26.02,
        "longitude": 22.40,
        "location": "Tsabong, Kgalagadi"
    }
}


@app.route("/")
def home():
    return jsonify({
        "status": "AgriSmart Botswana API is running"
    })


@app.route("/climate", methods=["POST"])
def climate():

    data = request.get_json()

    district = data.get("district")

    if district not in DISTRICTS:
        return jsonify({
            "error": "Unsupported district"
        }), 400

    place = DISTRICTS[district]

    try:

        response = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "daily": "temperature_2m_mean,precipitation_sum",
                "timezone": "Africa/Gaborone"
            },
            timeout=30
        )

        response.raise_for_status()

        daily = response.json()["daily"]

        temperatures = [
            t for t in daily["temperature_2m_mean"]
            if t is not None
        ]

        rainfall = [
            r for r in daily["precipitation_sum"]
            if r is not None
        ]

        avg_temp = sum(temperatures) / len(temperatures)
        total_rainfall = sum(rainfall)

        if avg_temp < 20:
            temp_category = "Low Temperature"
        elif avg_temp < 30:
            temp_category = "Moderate Temperature"
        else:
            temp_category = "High Temperature"

        if total_rainfall < 400:
            rainfall_category = "Low Rainfall"
            crops = ["Sorghum", "Millet", "Cowpea", "Groundnut"]

        elif total_rainfall < 800:
            rainfall_category = "Moderate Rainfall"
            crops = ["Maize", "Sunflower", "Watermelon"]

        else:
            rainfall_category = "High Rainfall"
            crops = ["Rice", "Cassava", "Vegetables"]

        return jsonify({
            "district": district,
            "location": place["location"],
            "temperature": temp_category,
            "rainfall": rainfall_category,
            "recommended_crops": crops
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

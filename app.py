from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://imewpqufkvhwzxjbspfe.supabase.co/rest/v1"
SUPABASE_KEY = "sb_publishable_urW9_MF4ZO3kN4u6apAvdw_NMqjG8cD"

DISTRICT_COORDINATES = {
    "Kgalagadi": {"lat": -26.02, "lon": 22.40},
    "Ghanzi": {"lat": -21.70, "lon": 21.65},
    "Chobe": {"lat": -17.80, "lon": 25.15},
    "North West": {"lat": -19.98, "lon": 23.42},
    "Central": {"lat": -22.33, "lon": 26.71},
    "Southern": {"lat": -24.40, "lon": 25.50},
    "Kweneng": {"lat": -24.60, "lon": 25.92},
    "Kgatleng": {"lat": -24.20, "lon": 26.83},
    "South East": {"lat": -24.65, "lon": 25.91},
    "North East": {"lat": -20.21, "lon": 27.51},
    "Northern": {"lat": -19.98, "lon": 23.42}
}


@app.route("/")
def home():
    return jsonify({
        "status": "AgriSmart Botswana API is running"
    })


@app.route("/analyse", methods=["POST"])
def analyse():

    try:

        data = request.get_json()
        district = data.get("district")

        if not district:
            return jsonify({
                "error": "District is required"
            }), 400

        # ========================
        # HISTORICAL DATA (SUPABASE)
        # ========================

        response = requests.get(
            f"{SUPABASE_URL}/climate_data?district=eq.{district}&order=year.asc",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )

        response.raise_for_status()

        records = response.json()

        if not records:
            return jsonify({
                "error": f"No climate data found for {district}"
            }), 404

        rainfall_values = []
        temperature_values = []

        for row in records:

            rainfall_values.append(
                float(row["rainfall_mm"])
            )

            temperature_values.append(
                float(row["avg_temperature_c"])
            )

        avg_rainfall = round(
            sum(rainfall_values) / len(rainfall_values),
            1
        )

        avg_temperature = round(
            sum(temperature_values) / len(temperature_values),
            1
        )

        # ========================
        # OPEN METEO DATA
        # ========================

        recent_temp = None
        recent_rain = None

        try:

            coords = DISTRICT_COORDINATES[district]

            meteo = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "current_weather": "true",
                    "daily": "precipitation_sum",
                    "timezone": "Africa/Gaborone"
                },
                timeout=20
            )

            meteo.raise_for_status()

            meteo_data = meteo.json()

            recent_temp = (
                meteo_data.get("current_weather", {})
                .get("temperature")
            )

            rainfall_daily = (
                meteo_data.get("daily", {})
                .get("precipitation_sum", [])
            )

            if rainfall_daily:
                recent_rain = rainfall_daily[0]

        except Exception:
            pass

        # ========================
        # RAINFALL ANALYSIS
        # ========================

        if avg_rainfall < 400:

            rainfall_category = "Low Rainfall"
            drought_risk = "High"
            flood_risk = "Low"

            crops = [
                "Sorghum",
                "Millet",
                "Cowpea",
                "Groundnut"
            ]

            practices = [
                "Mulching",
                "Rainwater harvesting",
                "Drip irrigation",
                "Early planting",
                "Drought resistant seed varieties"
            ]

        elif avg_rainfall < 800:

            rainfall_category = "Moderate Rainfall"
            drought_risk = "Moderate"
            flood_risk = "Low"

            crops = [
                "Maize",
                "Sunflower",
                "Groundnuts",
                "Watermelon"
            ]

            practices = [
                "Crop rotation",
                "Soil moisture conservation",
                "Monitor seasonal rainfall"
            ]

        else:

            rainfall_category = "High Rainfall"
            drought_risk = "Low"
            flood_risk = "Moderate"

            crops = [
                "Rice",
                "Cassava",
                "Vegetables",
                "Wet-Tolerant Maize"
            ]

            practices = [
                "Improve drainage",
                "Monitor fungal diseases",
                "Diversify crop production"
            ]

        # ========================
        # TEMPERATURE ANALYSIS
        # ========================

        if avg_temperature < 20:

            temperature_category = "Low Temperature"
            heat_risk = "Low"

        elif avg_temperature < 30:

            temperature_category = "Moderate Temperature"
            heat_risk = "Moderate"

        else:

            temperature_category = "High Temperature"
            heat_risk = "High"

        # ========================
        # TREND ANALYSIS
        # ========================

        rainfall_trend = "Stable"

        if rainfall_values[-1] > rainfall_valuesrainfall_trend = "Increasing"

        elif rainfall_values[-1] < rainfall_valuesrainfall_trend = "Decreasing"

        temperature_trend = "Stable"

        if temperature_values[-1] > temperature_valuestemperature_trend = "Increasing"

        elif temperature_values[-1] < temperature_valuestemperature_trend = "Decreasing"

        # ========================
        # AI RECOMMENDATION
        # ========================

        ai_advice = (
            f"Analysis of {len(records)} years of climate data "
            f"for {district} indicates {rainfall_category.lower()} "
            f"and {temperature_category.lower()}. "
            f"Drought risk is {drought_risk.lower()} while "
            f"heat stress risk is {heat_risk.lower()}. "
            f"Recommended crops include "
            f"{', '.join(crops)}. Farmers should focus on "
            f"{', '.join(practices[:3])} to improve resilience "
            f"and sustainability."
        )

        return jsonify({

            "district": district,

            "years_analysed": len(records),

            "historical_average_rainfall_mm":
                avg_rainfall,

            "historical_average_temperature_c":
                avg_temperature,

            "recent_temperature_c":
                recent_temp,

            "recent_rainfall_mm":
                recent_rain,

            "rainfall_category":
                rainfall_category,

            "temperature_category":
                temperature_category,

            "drought_risk":
                drought_risk,

            "heat_risk":
                heat_risk,

            "flood_risk":
                flood_risk,

            "rainfall_trend":
                rainfall_trend,

            "temperature_trend":
                temperature_trend,

            "recommended_crops":
                crops,

            "recommended_practices":
                practices,

            "ai_advice":
                ai_advice
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

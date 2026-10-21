from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://imewpqufkvhwzxjbspfe.supabase.co/rest/v1"
SUPABASE_KEY = "sb_publishable_urW9_MF4ZO3kN4u6apAvdw_NMqjG8cD"


@app.route("/")
def home():
    return jsonify({
        "status": "AgriSmart Botswana API is running"
    })


@app.route("/analyse", methods=["POST"])
def analyse():

    data = request.get_json()

    district = data.get("district")

    if not district:
        return jsonify({
            "error": "District is required"
        }), 400

    try:

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

        rainfall_values = [
            row["rainfall_mm"]
            for row in records
        ]

        temperature_values = [
            row["avg_temperature_c"]
            for row in records
        ]

        avg_rainfall = round(
            sum(rainfall_values) / len(rainfall_values),
            1
        )

        avg_temperature = round(
            sum(temperature_values) / len(temperature_values),
            1
        )

        # Rainfall Analysis
        if avg_rainfall < 400:

            rainfall_category = "Low Rainfall"
            drought_risk = "High"

            crops = [
                "Sorghum",
                "Millet",
                "Cowpea",
                "Groundnut"
            ]

            practices = [
                "Use drought-resistant seed varieties",
                "Apply mulching",
                "Harvest rainwater",
                "Use drip irrigation",
                "Plant immediately after effective rainfall"
            ]

        elif avg_rainfall < 800:

            rainfall_category = "Moderate Rainfall"
            drought_risk = "Moderate"

            crops = [
                "Maize",
                "Sunflower",
                "Groundnuts",
                "Watermelon"
            ]

            practices = [
                "Monitor rainfall patterns",
                "Use crop rotation",
                "Maintain soil moisture",
                "Diversify crop production"
            ]

        else:

            rainfall_category = "High Rainfall"
            drought_risk = "Low"

            crops = [
                "Rice",
                "Cassava",
                "Vegetables",
                "Wet-tolerant Maize"
            ]

            practices = [
                "Improve field drainage",
                "Monitor fungal diseases",
                "Take advantage of longer growing seasons"
            ]

        # Temperature Analysis
        if avg_temperature < 20:
            temperature_category = "Low Temperature"
            heat_risk = "Low"

        elif avg_temperature < 30:
            temperature_category = "Moderate Temperature"
            heat_risk = "Moderate"

        else:
            temperature_category = "High Temperature"
            heat_risk = "High"

        # Trend Analysis
        rainfall_trend = "Stable"

        if len(rainfall_values) > 1:

            if rainfall_values[-1] > rainfall_values[0]:
                rainfall_trend = "Increasing"

            elif rainfall_values[-1] < rainfall_values[0]:
                rainfall_trend = "Decreasing"

        temperature_trend = "Stable"

        if len(temperature_values) > 1:

            if temperature_values[-1] > temperature_values[0]:
                temperature_trend = "Increasing"

            elif temperature_values[-1] < temperature_values[0]:
                temperature_trend = "Decreasing"

        summary = (
            f"{district} shows {rainfall_category.lower()} "
            f"and {temperature_category.lower()}. "
            f"Drought risk is {drought_risk.lower()} "
            f"while heat risk is {heat_risk.lower()}."
        )

        return jsonify({

            "district": district,

            "years_analysed": len(records),

            "average_rainfall_mm": avg_rainfall,

            "average_temperature_c": avg_temperature,

            "rainfall_category": rainfall_category,

            "temperature_category": temperature_category,

            "drought_risk": drought_risk,

            "heat_risk": heat_risk,

            "rainfall_trend": rainfall_trend,

            "temperature_trend": temperature_trend,

            "recommended_crops": crops,

            "recommended_practices": practices,

            "summary": summary

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

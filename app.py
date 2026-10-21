from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Supabase Configuration
SUPABASE_URL = "https://imewpqufkvhwzxjbspfe.supabase.co/rest/v1"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

@app.route("/")
def home():
    return jsonify({
        "status": "AgriSmart Botswana API is running"
    })


@app.route("/analyse", methods=["POST"])
def analyse():

    data = request.get_json()
    district = data.get("district")

    try:

        # Fetch all historical records for district
        response = requests.get(
            f"{SUPABASE_URL}/climate_data?district=eq.{district}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )

        records = response.json()

        if not records:
            return jsonify({
                "error": "No climate data found"
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

        # Rainfall analysis
        if avg_rainfall < 400:
            rainfall_category = "Low Rainfall"
            drought_risk = "High"

            crops = [
                "Sorghum",
                "Millet",
                "Cowpea",
                "Groundnut"
            ]

            recommendations = [
                "Use drought-resistant crops",
                "Apply mulching",
                "Harvest rainwater",
                "Use drip irrigation where possible"
            ]

        elif avg_rainfall < 800:
            rainfall_category = "Moderate Rainfall"
            drought_risk = "Moderate"

            crops = [
                "Maize",
                "Sunflower",
                "Watermelon",
                "Groundnuts"
            ]

            recommendations = [
                "Use moisture conservation practices",
                "Monitor seasonal rainfall",
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

            recommendations = [
                "Improve drainage",
                "Monitor fungal diseases",
                "Take advantage of longer growing seasons"
            ]

        # Temperature analysis
        if avg_temperature < 20:
            temperature_category = "Low Temperature"
            heat_risk = "Low"

        elif avg_temperature < 30:
            temperature_category = "Moderate Temperature"
            heat_risk = "Moderate"

        else:
            temperature_category = "High Temperature"
            heat_risk = "High"

        # Trend analysis
        rainfall_trend = "Stable"

        if len(rainfall_values) >= 2:
            if rainfall_values[-1] < rainfall_valuesrainfall_trend = "Decreasing"
            elif rainfall_values[-1] > rainfall_valuesrainfall_trend = "Increasing"

        temperature_trend = "Stable"

        if len(temperature_values) >= 2:
            if temperature_values[-1] > temperature_valuestemperature_trend = "Increasing"
            elif temperature_values[-1] < temperature_valuestemperature_trend = "Decreasing"

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

            "recommended_practices": recommendations,

            "summary":
            f"{district} experiences {rainfall_category.lower()} "
            f"and {temperature_category.lower()}. "
            f"Drought risk is {drought_risk.lower()} "
            f"and heat risk is {heat_risk.lower()}."

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

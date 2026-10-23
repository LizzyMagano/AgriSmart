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

# ---------------------------------------------------------------
# TRANSLATION DICTIONARIES
# ---------------------------------------------------------------

TRANSLATIONS = {

    "en": {
        "low_rainfall": "Low Rainfall",
        "moderate_rainfall": "Moderate Rainfall",
        "high_rainfall": "High Rainfall",

        "low_temperature": "Low Temperature",
        "moderate_temperature": "Moderate Temperature",
        "high_temperature": "High Temperature",

        "high_risk": "High",
        "moderate_risk": "Moderate",
        "low_risk": "Low",

        "increasing": "Increasing",
        "decreasing": "Decreasing",
        "stable": "Stable",

        "advice_template": (
            "{district} shows {rainfall_category} and "
            "{temperature_category} conditions. "
            "Drought risk is {drought_risk} and heat risk is "
            "{heat_risk}. Recommended crops include "
            "{crops}. Farmers should focus on "
            "{practices} to improve resilience and "
            "sustainable production."
        ),

        "crops": {
            "low": ["Sorghum", "Millet", "Cowpea", "Groundnut"],
            "moderate": ["Maize", "Sunflower", "Groundnuts", "Watermelon"],
            "high": ["Rice", "Cassava", "Vegetables", "Wet-Tolerant Maize"]
        },

        "practices": {
            "low": [
                "Apply mulching",
                "Harvest rainwater",
                "Use drip irrigation",
                "Plant drought-resistant crops",
                "Plant immediately after effective rainfall"
            ],
            "moderate": [
                "Use crop rotation",
                "Monitor rainfall patterns",
                "Maintain soil moisture",
                "Diversify crop production"
            ],
            "high": [
                "Improve drainage",
                "Monitor fungal diseases",
                "Diversify crops"
            ]
        }
    },

    "tn": {
        "low_rainfall": "Pula e Nnye",
        "moderate_rainfall": "Pula e mo Magareng",
        "high_rainfall": "Pula e Ntsi",

        "low_temperature": "Mogote o o Kwa Tlase",
        "moderate_temperature": "Mogote o o mo Magareng",
        "high_temperature": "Mogote o o Kwa Godimo",

        "high_risk": "Godimo",
        "moderate_risk": "Magareng",
        "low_risk": "Tlase",

        "increasing": "E a Oketsega",
        "decreasing": "E a Fokotsega",
        "stable": "E Thebile",

        "advice_template": (
            "{district} e na le {rainfall_category} le "
            "{temperature_category}. "
            "Kotsi ya leuba ke {drought_risk} mme kotsi ya mogote ke "
            "{heat_risk}. Dijalo tse di tshitshintsweng di akaretsa "
            "{crops}. Balemi ba tshwanetse go tlhoma tlhoko mo "
            "{practices} go tokafatsa mamello le "
            "temo e e tswelelang."
        ),

        "crops": {
            "low": ["Mabele", "Leblele", "Dinawa", "Matonkomane"],
            "moderate": ["Mmidi", "Sunflower", "Matonkomane", "Legapu"],
            "high": ["Raese", "Cassava", "Merogo", "Mmidi o o Emelang Metsi"]
        },

        "practices": {
            "low": [
                "Dirisa mulch",
                "Kgapela pula",
                "Dirisa drip irrigation",
                "Jala dijalo tse di emelang leuba",
                "Jala ka bonako morago ga pula e e lekaneng"
            ],
            "moderate": [
                "Dirisa go fetola dijalo",
                "Lekola mokgwa wa pula",
                "Boloka metsi mo mmung",
                "Farologanya temo ya dijalo"
            ],
            "high": [
                "Tokafatsa go tsamaisa metsi",
                "Lekola malwetse a fungal",
                "Farologanya dijalo"
            ]
        }
    }
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

        if not data:
            return jsonify({
                "error": "Request body required"
            }), 400

        district = data.get("district")
        lang = data.get("language", "en").lower()

        if lang not in TRANSLATIONS:
            lang = "en"

        t = TRANSLATIONS[lang]

        if not district:
            return jsonify({
                "error": "District is required"
            }), 400

        # HISTORICAL DATA FROM SUPABASE

        response = requests.get(
            f"{SUPABASE_URL}/climate_data?district=eq.{district}&order=year.asc",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=30
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

        # CURRENT DATA FROM OPEN-METEO

        recent_temp = None
        recent_rain = None

        try:

            coords = DISTRICT_COORDINATES.get(district)

            if coords:

                meteo_response = requests.get(
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

                meteo_response.raise_for_status()

                meteo_data = meteo_response.json()

                recent_temp = (
                    meteo_data.get("current_weather", {})
                    .get("temperature")
                )

                daily_rain = (
                    meteo_data.get("daily", {})
                    .get("precipitation_sum", [])
                )

                if daily_rain:
                    recent_rain = daily_rain[0]

        except Exception:
            pass

        # RAINFALL ANALYSIS

        if avg_rainfall < 400:

            rainfall_category = t["low_rainfall"]
            drought_risk = t["high_risk"]
            flood_risk = t["low_risk"]

            crops = t["crops"]["low"]
            practices = t["practices"]["low"]

        elif avg_rainfall < 800:

            rainfall_category = t["moderate_rainfall"]
            drought_risk = t["moderate_risk"]
            flood_risk = t["low_risk"]

            crops = t["crops"]["moderate"]
            practices = t["practices"]["moderate"]

        else:

            rainfall_category = t["high_rainfall"]
            drought_risk = t["low_risk"]
            flood_risk = t["moderate_risk"]

            crops = t["crops"]["high"]
            practices = t["practices"]["high"]

        # TEMPERATURE ANALYSIS

        if avg_temperature < 20:

            temperature_category = t["low_temperature"]
            heat_risk = t["low_risk"]

        elif avg_temperature < 30:

            temperature_category = t["moderate_temperature"]
            heat_risk = t["moderate_risk"]

        else:

            temperature_category = t["high_temperature"]
            heat_risk = t["high_risk"]

        # TREND ANALYSIS

        rainfall_trend = t["stable"]

        if len(rainfall_values) > 1:

            first_rainfall = rainfall_values[0]
            last_rainfall = rainfall_values[-1]

            if last_rainfall > first_rainfall:
                rainfall_trend = t["increasing"]

            elif last_rainfall < first_rainfall:
                rainfall_trend = t["decreasing"]

        temperature_trend = t["stable"]

        if len(temperature_values) > 1:

            first_temperature = temperature_values[0]
            last_temperature = temperature_values[-1]

            if last_temperature > first_temperature:
                temperature_trend = t["increasing"]

            elif last_temperature < first_temperature:
                temperature_trend = t["decreasing"]

        # AI-STYLE ADVICE

        ai_advice = t["advice_template"].format(
            district=district,
            rainfall_category=rainfall_category,
            temperature_category=temperature_category,
            drought_risk=drought_risk,
            heat_risk=heat_risk,
            crops=", ".join(crops),
            practices=", ".join(practices[:3])
        )

        return jsonify({

            "district": district,
            "language": lang,

            "years_analysed": len(records),

            "historical_average_rainfall_mm": avg_rainfall,

            "historical_average_temperature_c": avg_temperature,

            "recent_temperature_c": recent_temp,

            "recent_rainfall_mm": recent_rain,

            "rainfall_category": rainfall_category,

            "temperature_category": temperature_category,

            "drought_risk": drought_risk,

            "heat_risk": heat_risk,

            "flood_risk": flood_risk,

            "rainfall_trend": rainfall_trend,

            "temperature_trend": temperature_trend,

            "recommended_crops": crops,

            "recommended_practices": practices,

            "ai_advice": ai_advice

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

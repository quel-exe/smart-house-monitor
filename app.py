from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Load local development credentials before the Firebase and ThingSpeak helpers
# read their environment variables.  The .env file is ignored by Git.
load_dotenv()

from services.firebase import FirebaseError, get_house_data, set_device_state
from services.thingspeak import ThingSpeakError, get_sensor_history, send_sensor_reading


app = Flask(__name__)


@app.route("/")
def dashboard():
    """Show the latest Smart House data from Firebase."""
    house_data = get_house_data()
    return render_template(
        "dashboard.html",
        sensor_data=house_data["sensors"],
        device_data=house_data["devices"],
        firebase_error=house_data["error"],
    )


@app.post("/api/devices/<device_name>")
def update_device(device_name):
    """Save a future actuator's on/off state to Firebase."""
    request_data = request.get_json(silent=True) or {}
    enabled = request_data.get("enabled")

    if not isinstance(enabled, bool):
        return jsonify({"error": "The 'enabled' value must be true or false."}), 400

    try:
        set_device_state(device_name, enabled)
    except FirebaseError as error:
        return jsonify({"error": str(error)}), 500

    return jsonify({"device": device_name, "enabled": enabled})


@app.post("/api/thingspeak/update")
def update_thingspeak():
    """Copy the current Firebase sensor reading to ThingSpeak history."""
    house_data = get_house_data()
    if house_data["error"]:
        return jsonify({"error": house_data["error"]}), 503

    try:
        result = send_sensor_reading(house_data["raw_sensors"])
    except ThingSpeakError as error:
        return jsonify({"error": str(error)}), 502

    return jsonify(result), 200


@app.get("/api/thingspeak/history")
def thingspeak_history():
    """Return recent ThingSpeak readings for the dashboard charts and table."""
    try:
        results = int(request.args.get("results", 20))
    except ValueError:
        return jsonify({"error": "The results value must be a number."}), 400

    if not 1 <= results <= 100:
        return jsonify({"error": "The results value must be between 1 and 100."}), 400

    try:
        return jsonify(get_sensor_history(results))
    except ThingSpeakError as error:
        return jsonify({"error": str(error)}), 502


if __name__ == "__main__":
    app.run(debug=True)

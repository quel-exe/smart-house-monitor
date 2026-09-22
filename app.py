from flask import Flask, jsonify, render_template, request

from services.firebase import FirebaseError, get_house_data, set_device_state


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


if __name__ == "__main__":
    app.run(debug=True)

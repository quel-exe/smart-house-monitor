"""Small Firebase Realtime Database helpers for the Flask application."""

import os

import firebase_admin
from firebase_admin import credentials, db


# This URL identifies the database; it is not a private key.
DATABASE_URL = os.getenv(
    "FIREBASE_DATABASE_URL",
    "https://smart-house-monitoring-d931a-default-rtdb.asia-southeast1.firebasedatabase.app",
)


class FirebaseError(Exception):
    """Raised when the application cannot read or write Firebase data."""


def _get_database():
    """Initialize Firebase once and return a Realtime Database reference."""
    try:
        firebase_admin.get_app()
    except ValueError:
        # GOOGLE_APPLICATION_CREDENTIALS must point to the private JSON key file.
        # The key is deliberately not stored in this project.
        credential = credentials.ApplicationDefault()
        firebase_admin.initialize_app(credential, {"databaseURL": DATABASE_URL})

    return db.reference("/")


def get_house_data():
    """Read dashboard values, keeping the page usable if Firebase is unavailable."""
    fallback_data = {
        "sensors": {
            "temperature": "--",
            "humidity": "--",
            "presence": "Unknown",
            "motion": "Unknown",
        },
        "devices": {"light": False, "fan": False, "alarm": False},
        "error": None,
    }

    try:
        data = _get_database().get() or {}
        sensors = data.get("sensors", {})
        devices = data.get("devices", {})

        return {
            "sensors": {
                "temperature": sensors.get("temperature", "--"),
                "humidity": sensors.get("humidity", "--"),
                "presence": "Human detected" if sensors.get("pir") else "No one detected",
                "motion": "Motion detected" if sensors.get("motion") else "No motion",
            },
            "devices": {
                "light": devices.get("light", False),
                "fan": devices.get("fan", False),
                "alarm": devices.get("alarm", False),
            },
            # Keep the original Firebase values available for other services.
            "raw_sensors": {
                "temperature": sensors.get("temperature"),
                "humidity": sensors.get("humidity"),
                "pir": sensors.get("pir"),
                "motion": sensors.get("motion"),
            },
            "error": None,
        }
    except Exception as error:
        fallback_data["error"] = f"Firebase could not be reached: {error}"
        return fallback_data


def set_device_state(device_name, enabled):
    """Write one supported device state to Firebase."""
    allowed_devices = {"light", "fan", "alarm"}
    if device_name not in allowed_devices:
        raise FirebaseError("Unknown device.")

    try:
        _get_database().child("devices").child(device_name).set(enabled)
    except Exception as error:
        raise FirebaseError(f"Could not update {device_name}: {error}") from error

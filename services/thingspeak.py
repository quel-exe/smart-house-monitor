"""ThingSpeak HTTP API helpers for historical Smart House sensor readings."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


UPDATE_URL = "https://api.thingspeak.com/update.json"
CHANNEL_URL = "https://api.thingspeak.com/channels"


class ThingSpeakError(Exception):
    """Raised when a reading cannot be sent to ThingSpeak."""


def _get_configuration():
    """Read required ThingSpeak settings without storing secrets in code."""
    channel_id = os.getenv("THINGSPEAK_CHANNEL_ID")
    write_api_key = os.getenv("THINGSPEAK_WRITE_API_KEY")

    if not channel_id or not write_api_key:
        raise ThingSpeakError(
            "ThingSpeak is not configured. Set THINGSPEAK_CHANNEL_ID and "
            "THINGSPEAK_WRITE_API_KEY."
        )

    return channel_id, write_api_key


def _get_read_configuration():
    """Read the channel settings needed to retrieve historical feeds."""
    channel_id = os.getenv("THINGSPEAK_CHANNEL_ID")
    read_api_key = os.getenv("THINGSPEAK_READ_API_KEY")

    if not channel_id:
        raise ThingSpeakError("ThingSpeak is not configured. Set THINGSPEAK_CHANNEL_ID.")

    return channel_id, read_api_key


def _sensor_number(sensor_values, name):
    """Ensure a Firebase sensor value is a real number."""
    try:
        return float(sensor_values[name])
    except (KeyError, TypeError, ValueError) as error:
        raise ThingSpeakError(f"Firebase does not have a valid {name} reading.") from error


def send_sensor_reading(sensor_values):
    """Send the current Firebase sensor values to ThingSpeak fields 1 to 4."""
    channel_id, write_api_key = _get_configuration()
    payload = {
        "api_key": write_api_key,
        "field1": _sensor_number(sensor_values, "temperature"),
        "field2": _sensor_number(sensor_values, "humidity"),
        "field3": int(bool(sensor_values.get("pir"))),
        "field4": _sensor_number(sensor_values, "ldr"),
    }

    request = Request(
        UPDATE_URL,
        data=urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
            if response.status != 200:
                raise ThingSpeakError("ThingSpeak returned an unsuccessful response.")
    except HTTPError as error:
        raise ThingSpeakError(f"ThingSpeak rejected the update (HTTP {error.code}).") from error
    except URLError as error:
        raise ThingSpeakError("Could not reach ThingSpeak. Check your internet connection.") from error
    except TimeoutError as error:
        raise ThingSpeakError("ThingSpeak did not respond before the request timed out.") from error

    try:
        result = json.loads(response_body)
        entry_id = result.get("entry_id")
    except json.JSONDecodeError as error:
        raise ThingSpeakError("ThingSpeak returned an unexpected response.") from error

    if not entry_id:
        raise ThingSpeakError(
            "ThingSpeak did not create an entry. Wait at least 15 seconds before trying again."
        )

    return {
        "channel_id": channel_id,
        "entry_id": entry_id,
        "fields": {key: value for key, value in payload.items() if key != "api_key"},
    }


def _feed_number(feed, field_name):
    """Convert a ThingSpeak feed field to a number, preserving missing data."""
    value = feed.get(field_name)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_sensor_history(results=20):
    """Retrieve recent house readings from a ThingSpeak channel."""
    channel_id, read_api_key = _get_read_configuration()
    query = {"results": results}
    if read_api_key:
        query["api_key"] = read_api_key

    request = Request(f"{CHANNEL_URL}/{channel_id}/feeds.json?{urlencode(query)}")
    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
            if response.status != 200:
                raise ThingSpeakError("ThingSpeak returned an unsuccessful response.")
    except HTTPError as error:
        raise ThingSpeakError(f"ThingSpeak could not read the channel (HTTP {error.code}).") from error
    except URLError as error:
        raise ThingSpeakError("Could not reach ThingSpeak. Check your internet connection.") from error
    except TimeoutError as error:
        raise ThingSpeakError("ThingSpeak did not respond before the request timed out.") from error

    try:
        payload = json.loads(response_body)
        feeds = payload.get("feeds", [])
    except (AttributeError, json.JSONDecodeError) as error:
        raise ThingSpeakError("ThingSpeak returned an unexpected response.") from error

    if not isinstance(feeds, list):
        raise ThingSpeakError("ThingSpeak returned invalid feed data.")

    return {
        "channel_id": channel_id,
        "feeds": [
            {
                "entry_id": feed.get("entry_id"),
                "created_at": feed.get("created_at"),
                "temperature": _feed_number(feed, "field1"),
                "humidity": _feed_number(feed, "field2"),
                "motion": _feed_number(feed, "field3"),
                "light_level": _feed_number(feed, "field4"),
            }
            for feed in feeds
        ],
    }

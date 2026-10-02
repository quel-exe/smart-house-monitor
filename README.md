# Smart House Monitoring System

A Flask dashboard for an Embedded Systems smart-house project. Firebase stores the current house state; ThingSpeak stores sensor history for charts and a readings table.

## Project status

The current Flask, Firebase, and ThingSpeak integration has been tested successfully:

- The dashboard reads live sensor and actuator states from Firebase.
- The four room-light switches write their states back to Firebase.
- The dashboard sends a current reading to ThingSpeak on demand.
- The dashboard loads the 20 most recent ThingSpeak readings into charts and a table.

## Project structure

```text
smart-house-monitor/
├── app.py
├── firebase-seed.json
├── requirements.txt
├── .gitignore
├── templates/
│   └── dashboard.html
├── static/
│   ├── css/style.css
│   └── js/dashboard.js
└── services/
    ├── firebase.py
    └── thingspeak.py
```

## Run locally

1. Make sure Python 3.9 or newer is installed.
2. Create and activate a virtual environment (recommended):

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Set the path to your Firebase service-account JSON key for this PowerShell session. Keep this private file outside the project folder:

   ```powershell
   $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\your-service-account-key.json"
   ```

   The database URL used by this project is already configured. To use a different database later, set `FIREBASE_DATABASE_URL` before running the app.

5. Configure ThingSpeak for this PowerShell session:

   ```powershell
   $env:THINGSPEAK_CHANNEL_ID = "your-channel-id"
   $env:THINGSPEAK_WRITE_API_KEY = "your-write-api-key"
   $env:THINGSPEAK_READ_API_KEY = "your-read-api-key"
   ```

   `THINGSPEAK_CHANNEL_ID` and `THINGSPEAK_WRITE_API_KEY` are required to send readings. `THINGSPEAK_READ_API_KEY` is required only for a private channel; leave it unset if the channel is public. Never add either key to source code, Git, or frontend JavaScript.

6. Start the application:

   ```powershell
   python app.py
   ```

7. Open http://127.0.0.1:5000 in your browser.

## Firebase replacement data

Replace the placeholder data at the root of your Firebase Realtime Database with the contents of [firebase-seed.json](firebase-seed.json). The ESP8266 should then update the same keys:

```json
{
  "sensors": {
    "temperature": 27.4,
    "humidity": 68,
    "pir": false,
    "ldr": 740
  },
  "devices": {
    "room_1_light": false,
    "room_2_light": false,
    "room_3_light": false,
    "room_4_light": false,
    "room_5_light": false,
    "door_servo": false,
    "motion_led": false,
    "outside_light": false
  }
}
```

`pir` is `true` when motion is detected in front of the door. At that time the ESP8266 should set `door_servo` and `motion_led` to `true`. It should set `outside_light` based on the LDR reading. `room_1_light` through `room_5_light` are manual dashboard switches.

The Firebase root should contain only the `sensors` and `devices` objects above. Export the root as a backup before replacing old placeholder data.

## Configure a ThingSpeak channel

1. Create a channel in ThingSpeak named `Smart House Monitoring`.
2. Enable and name the fields exactly as follows:
   - Field 1: Temperature
   - Field 2: Humidity
   - Field 3: PIR motion (`1` for detected, `0` for no motion)
   - Field 4: LDR light level
3. In the channel's **API Keys** tab, copy the Channel ID, Write API Key, and (for a private channel) Read API Key.
4. Set the matching environment variables as shown above.

## Test a ThingSpeak update

With the Flask app running and Firebase values available, click **Send current reading** on the dashboard. The button sends the current Firebase values to ThingSpeak:

- `field1`: temperature
- `field2`: humidity
- `field3`: PIR motion (`1` for detected, `0` for no motion)
- `field4`: LDR light level

You can also test the Flask endpoint from PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/api/thingspeak/update"
```

ThingSpeak free channels normally require at least 15 seconds between updates. Open the channel's **Private View** or **Public View** to confirm a new entry and its charts.

## View history in the dashboard

The dashboard loads the 20 most recent ThingSpeak readings into four charts and a table. Use **Refresh history** to retrieve the newest entries. For a private channel, set `THINGSPEAK_READ_API_KEY`; for a public channel, this setting is optional. The read key stays on the Flask server and is never exposed to the browser.

The dashboard reads history through `GET /api/thingspeak/history?results=20`. It does not expose a ThingSpeak API key to the browser.

## Current features

- Dashboard reads DHT11 temperature/humidity, PIR motion, and LDR light level from Firebase.
- The room-light switches write `devices/room_1_light` through `devices/room_5_light` to Firebase.
- The dashboard shows the automatic door-servo, motion-indicator LED, and exterior LED states.
- A button and Flask route that manually copies a Firebase sensor reading to ThingSpeak.
- ThingSpeak history charts and a timestamped table are shown in the dashboard.

## Next phase: ESP8266 integration

- Connect the DHT11, PIR, LDR, door servo, and LEDs to the ESP8266.
- Have the ESP8266 update `sensors/temperature`, `sensors/humidity`, `sensors/pir`, and `sensors/ldr` in Firebase.
- Add automatic, rate-limited ThingSpeak updates when new Firebase sensor values arrive.
- Let the ESP8266 set `devices/door_servo`, `devices/motion_led`, and `devices/outside_light`; read `devices/room_1_light` through `devices/room_5_light` for the manual room LEDs.

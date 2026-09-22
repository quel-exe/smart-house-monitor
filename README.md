# Smart House Monitoring System

A beginner-friendly Flask dashboard for an Embedded Systems school project. Firebase stores the live state, while ThingSpeak stores historical sensor readings for charts.

## Project status

The current Flask, Firebase, and ThingSpeak integration has been tested successfully:

- The dashboard reads live sensor values from Firebase.
- Dashboard controls write device states to Firebase.
- The dashboard can manually copy the current Firebase sensor reading to ThingSpeak.

## Project structure

```text
smart-house-monitor/
├── app.py
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
   ```

   These values are required only when sending a historical reading. Never add the Write API Key to source code, Git, or frontend JavaScript.

6. Start the application:

   ```powershell
   python app.py
   ```

7. Open http://127.0.0.1:5000 in your browser.

## Configure a ThingSpeak channel

1. Create a channel in ThingSpeak named `Smart House Monitoring`.
2. Enable and name the fields exactly as follows:
   - Field 1: Temperature
   - Field 2: Humidity
   - Field 3: PIR
   - Field 4: Motion
3. In the channel's **API Keys** tab, copy the Channel ID and **Write API Key**.
4. Set `THINGSPEAK_CHANNEL_ID` and `THINGSPEAK_WRITE_API_KEY` as shown above.

## Test a ThingSpeak update

With the Flask app running and Firebase values available, click **Send current reading** on the dashboard. The button sends the current Firebase values to ThingSpeak:

- `field1`: temperature
- `field2`: humidity
- `field3`: PIR (`1` for detected, `0` for not detected)
- `field4`: motion (`1` for detected, `0` for not detected)

You can also test the Flask endpoint from PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/api/thingspeak/update"
```

ThingSpeak free channels normally require at least 15 seconds between updates. Open the channel's **Private View** or **Public View** to confirm a new entry and its charts.

## Current features

- Dashboard reads temperature, humidity, PIR, and motion values from Firebase.
- Lights, fan, and alarm buttons write their on/off state to Firebase.
- A button and Flask route that manually copies a Firebase sensor reading to ThingSpeak.

## Next phase: ESP32 integration

- Connect the DHT, PIR, and motion sensors to the ESP32.
- Have the ESP32 update `sensors/temperature`, `sensors/humidity`, `sensors/pir`, and `sensors/motion` in Firebase.
- Add automatic, rate-limited ThingSpeak updates when new Firebase sensor values arrive.
- Replace placeholder device controls with real ESP32 actuator commands for lights, fan, and alarm.
- Embed historical ThingSpeak charts in the Flask dashboard.

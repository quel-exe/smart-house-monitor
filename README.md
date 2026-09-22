# Smart House Monitoring System

A beginner-friendly Flask dashboard for an Embedded Systems school project. This first phase provides a local web interface with sample sensor readings and future device controls.

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

5. Start the application:

   ```powershell
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser.

## Current features

- Dashboard reads temperature, humidity, PIR, and motion values from Firebase.
- Lights, fan, and alarm buttons write their on/off state to Firebase.
- A simple structure ready for ESP32 and ThingSpeak additions later.

## Phase 2 ideas

- Connect the ESP32 and send real sensor readings to Firebase.
- Send selected data to ThingSpeak for charts and analysis.
- Replace placeholder controls with real actuator commands.
- Add validation, status/error messages, and historical charts.

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

3. Install the dependency:

   ```powershell
   pip install -r requirements.txt
   ```

4. Start the application:

   ```powershell
   python app.py
   ```

5. Open http://127.0.0.1:5000 in your browser.

## Current features

- Dashboard with placeholder temperature, humidity, presence, and motion data.
- Visual controls for lights, fan, and alarm. They only update the page while the browser is open.
- A simple structure ready for Firebase and ThingSpeak service code later.

## Phase 2 ideas

- Connect the ESP32 and send real sensor readings.
- Store and retrieve readings with Firebase.
- Send selected data to ThingSpeak for charts and analysis.
- Replace placeholder controls with real actuator commands.
- Add validation, status/error messages, and historical charts.

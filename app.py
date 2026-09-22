from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def dashboard():
    """Show the dashboard with sample values for the first project phase."""
    sensor_data = {
        "temperature": 26.5,
        "humidity": 62,
        "presence": "No one detected",
        "motion": "No motion",
    }
    return render_template("dashboard.html", sensor_data=sensor_data)


if __name__ == "__main__":
    app.run(debug=True)

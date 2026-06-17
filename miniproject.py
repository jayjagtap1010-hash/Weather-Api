from flask import Flask, request, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = "bebaa6554c80601364dc39ef10e6f950"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Advanced Weather App</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:'Segoe UI',sans-serif;
}

body{
    min-height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    background:linear-gradient(135deg,#00c6ff,#0072ff);
    padding:20px;
}

.container{
    width:100%;
    max-width:550px;
    background:rgba(255,255,255,0.15);
    backdrop-filter:blur(15px);
    border-radius:25px;
    padding:30px;
    text-align:center;
    color:white;
    box-shadow:0 8px 32px rgba(0,0,0,0.2);
}

h1{
    margin-bottom:20px;
}

.search-box{
    display:flex;
    gap:10px;
    margin-bottom:20px;
}

.search-box input{
    flex:1;
    padding:12px;
    border:none;
    border-radius:12px;
    outline:none;
    font-size:16px;
}

.search-box button{
    padding:12px 20px;
    border:none;
    border-radius:12px;
    background:#ff9800;
    color:white;
    font-weight:bold;
    cursor:pointer;
}

.search-box button:hover{
    background:#ff7700;
}

.icon{
    font-size:80px;
}

.city{
    font-size:28px;
    margin-top:10px;
}

.temp{
    font-size:55px;
    font-weight:bold;
}

.desc{
    margin-top:5px;
    text-transform:capitalize;
}

.details{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:12px;
    margin-top:25px;
}

.card{
    background:rgba(255,255,255,0.2);
    padding:15px;
    border-radius:15px;
}

.card h3{
    font-size:15px;
}

.card p{
    margin-top:8px;
    font-size:18px;
    font-weight:bold;
}

.error{
    color:#ffd6d6;
    font-weight:bold;
    margin-top:15px;
}

</style>
</head>

<body>

<div class="container">

<h1>🌦 Advanced Weather App</h1>

<form method="POST" class="search-box">
<input type="text" name="city" placeholder="Enter city name..." required>
<button type="submit">Search</button>
</form>

{% if weather %}

<div class="icon">{{ weather.icon }}</div>

<div class="city">{{ weather.city }}, {{ weather.country }}</div>

<div class="temp">{{ weather.temp }}°C</div>

<div class="desc">{{ weather.description }}</div>

<div class="details">

<div class="card">
<h3>💧 Humidity</h3>
<p>{{ weather.humidity }}%</p>
</div>

<div class="card">
<h3>🌬 Wind</h3>
<p>{{ weather.wind }} m/s</p>
</div>

<div class="card">
<h3>🌡 Feels Like</h3>
<p>{{ weather.feels }}°C</p>
</div>

<div class="card">
<h3>📍 State</h3>
<p>{{ weather.state }}</p>
</div>

<div class="card">
<h3>🌍 Latitude</h3>
<p>{{ weather.lat }}</p>
</div>

<div class="card">
<h3>🌎 Longitude</h3>
<p>{{ weather.lon }}</p>
</div>

<div class="card">
<h3>🌅 Sunrise</h3>
<p>{{ weather.sunrise }}</p>
</div>

<div class="card">
<h3>🌇 Sunset</h3>
<p>{{ weather.sunset }}</p>
</div>

<div class="card">
<h3>🕒 Local Time</h3>
<p>{{ weather.local_time }}</p>
</div>

<div class="card">
<h3>☁ Pressure</h3>
<p>{{ weather.pressure }} hPa</p>
</div>

</div>

{% endif %}

{% if error %}
<p class="error">{{ error }}</p>
{% endif %}

</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    error = None

    if request.method == "POST":

        city = request.form["city"]

        try:

            weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={API_KEY}&units=metric"
            )

            response = requests.get(weather_url)
            data = response.json()

            if data.get("cod") == 200:

                geo_url = (
                    f"https://api.openweathermap.org/geo/1.0/direct"
                    f"?q={city}&limit=1&appid={API_KEY}"
                )

                geo_data = requests.get(geo_url).json()

                state = "N/A"
                if geo_data:
                    state = geo_data[0].get("state", "N/A")

                description = data["weather"][0]["description"].lower()

                icon = "☀️"

                if "cloud" in description:
                    icon = "☁️"
                elif "rain" in description:
                    icon = "🌧️"
                elif "thunder" in description:
                    icon = "⛈️"
                elif "snow" in description:
                    icon = "❄️"
                elif "mist" in description:
                    icon = "🌫️"

                timezone_offset = data["timezone"]

                local_time = datetime.utcfromtimestamp(
                    datetime.utcnow().timestamp() + timezone_offset
                ).strftime("%I:%M %p")

                sunrise = datetime.utcfromtimestamp(
                    data["sys"]["sunrise"] + timezone_offset
                ).strftime("%I:%M %p")

                sunset = datetime.utcfromtimestamp(
                    data["sys"]["sunset"] + timezone_offset
                ).strftime("%I:%M %p")

                weather = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "state": state,
                    "temp": round(data["main"]["temp"]),
                    "feels": round(data["main"]["feels_like"]),
                    "description": description,
                    "humidity": data["main"]["humidity"],
                    "wind": data["wind"]["speed"],
                    "pressure": data["main"]["pressure"],
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"],
                    "sunrise": sunrise,
                    "sunset": sunset,
                    "local_time": local_time,
                    "icon": icon
                }

            else:
                error = "City not found!"

        except Exception as e:
            error = f"Error: {e}"

    return render_template_string(
        HTML,
        weather=weather,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
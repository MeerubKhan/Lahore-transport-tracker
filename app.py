# Transport Tracker - Lahore
# My project to compare rickshaw, uber, indrive, metro, speedo
import random
import folium
from flask import Flask,render_template, request
#flask : that creates your web app
#render_template: sends an html file to the browser
#request: read the input typed in the browser
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ORS_API_KEY")

app=Flask(__name__)

LAT_MIN=31.25
LAT_MAX=31.75
LON_MIN=74.01
LON_MAX=74.65    

@app.route("/" ,methods=['GET','POST']) #decorator
#When someone visits the " / " page (the homepage), run the function below it
#get means that user just came on the website 
#post means that user has filled the form

# A decorator works by wrapping the function that comes right after it. It's saying:
# "Take the next function I see and apply this route to it"
# If you put code between the decorator and the function — Python gets confused.
# It sees the decorator, expects a function next, but finds LAT_MIN = 31.25 instead. That's a syntax error.
# LAT_MIN=31.25
# LAT_MAX=31.75
# LON_MIN=74.01
# LON_MAX=74.65    


def home():
    results=None
    start=" "
    destination=" "
    distance=None
    duration=None
    error=None
    route_map=None
    if request.method=="POST":
       start=request.form["start"]
       destination=request.form["destination"]
       distance,duration,route_map=get_route_info(start,destination)
       if distance is None:
            error="Could not find route. Please try again or be more specific."
            return render_template("index.html",results=None,error=error,start=start,destination=destination,distance=None,duration=None,route_map=None)
       transports = {
            "Local Rickshaw":   {"price": f"Rs.{int(distance*50)}-{int(distance*30)}", "time": f"{int((distance/25)*60)} mins", "comfort": "Low"},
            "InDrive Car":      {"price": f"Rs.{int(distance*30)}-{int(distance*50)}", "time": f"{int((distance/35)*60)} mins", "comfort": "High"},
            "InDrive Rickshaw": {"price": f"Rs.{int(distance*25)}-{int(distance*35)}", "time": f"{int((distance/35)*60)} mins", "comfort": "High"},
            "Bykea":            {"price": f"Rs.{int(distance*13)}-{int(distance*15)}", "time": f"{int((distance/40)*60)} mins", "comfort": "Medium"},
            "Yango":            {"price": f"Rs.{int(distance*25)}-{int(distance*35)}", "time": f"{int((distance/35)*60)} mins", "comfort": "High"},
            "Metro":            {"price": "Rs.30-50",                                   "time": f"{int((distance/18)*60)} mins", "comfort": "Medium"},
        }
       results=transports
    return render_template("index.html",results=results,start=start,destination=destination,distance=distance,duration=duration,route_map=route_map)

  

def get_route_info(start, destination):
    try:
        # geocode start location
        response = requests.get(
            f'https://api.openrouteservice.org/geocode/search?api_key={API_KEY}'
            f'&text={start}+Lahore'
            f'&boundary.rect.min_lat={LAT_MIN}&boundary.rect.max_lat={LAT_MAX}'
            f'&boundary.rect.min_lon={LON_MIN}&boundary.rect.max_lon={LON_MAX}'
            f'&size=1'
        )
        data = response.json()
        start_cords = data['features'][0]['geometry']['coordinates']

        # geocode destination
        response1 = requests.get(
            f'https://api.openrouteservice.org/geocode/search?api_key={API_KEY}'
            f'&text={destination}+Lahore'
            f'&boundary.rect.min_lat={LAT_MIN}&boundary.rect.max_lat={LAT_MAX}'
            f'&boundary.rect.min_lon={LON_MIN}&boundary.rect.max_lon={LON_MAX}'
            f'&size=1'
        )
        data1 = response1.json()
        dest_cords = data1['features'][0]['geometry']['coordinates']

        # get directions
        raw_directions = requests.get(
            f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={API_KEY}'
            f'&start={start_cords[0]},{start_cords[1]}'
            f'&end={dest_cords[0]},{dest_cords[1]}'
        )
        data = raw_directions.json()

        geometry = data['features'][0]['geometry']['coordinates']
        distance_km = round(data['features'][0]['properties']['segments'][0]['distance'] / 1000, 1)
        duration_min = int(data['features'][0]['properties']['segments'][0]['duration'] / 60)

        # build map
        center_lat = (start_cords[1] + dest_cords[1]) / 2
        center_lon = (start_cords[0] + dest_cords[0]) / 2

        route_map = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="CartoDB voyager")

        # markers
        folium.Marker(
            [start_cords[1], start_cords[0]],
            tooltip=f"Start: {start}",
            icon=folium.Icon(color='green', icon='home')
        ).add_to(route_map)

        folium.Marker(
            [dest_cords[1], dest_cords[0]],
            tooltip=f"Destination: {destination}",
            icon=folium.Icon(color='red', icon='flag')
        ).add_to(route_map)

        # route line
        swap_geometry = [[point[1], point[0]] for point in geometry]
        folium.PolyLine(locations=swap_geometry, color="#4A90E2", weight=5, opacity=0.8).add_to(route_map)

        # fit map to route
        route_map.fit_bounds([
            [min(p[0] for p in swap_geometry), min(p[1] for p in swap_geometry)],
            [max(p[0] for p in swap_geometry), max(p[1] for p in swap_geometry)]
        ])

        map_html = route_map._repr_html_()
        return distance_km, duration_min, map_html

    except Exception as e:
        return None, None, None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

   

   

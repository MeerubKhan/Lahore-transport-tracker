# Transport Tracker - Lahore
# My project to compare rickshaw, uber, indrive, metro, speedo
import random
from flask import Flask,render_template, request
#flask : that creates your web app
#render_template: sends an html file to the browser
#request: read the input typed in the browser
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ORS_API_KEY")
print("API KEY LOADED:", bool(API_KEY))

app=Flask(__name__)


@app.route("/" ,methods=['GET','POST']) #decorator
#When someone visits the " / " page (the homepage), run the function below it
#get means that user just came on the website 
#post means that user has filled the form

def home():
    results=None
    start=" "
    destination=" "
    distance=None
    duration=None
    error=None
    if request.method=="POST":
       start=request.form["start"]
       destination=request.form["destination"]
       distance,duration=get_route_info(start,destination)
       if distance is None:
            error="Could not find route. Please try again or be more specific."
            return render_template("index.html",results=None,error=error,start=start,destination=destination,distance=None,duration=None)
       transports={
          "Local Rickshaw": {"price" :f"Rs.{int(distance*50)}-{int(distance*80)}" , "time" :f"{int((distance/25)*60)}mins", "comfort" : "Low"},
          "InDrive Car" : {"price" : f"Rs.{int(distance*30)}-{int(distance*50)}" , "time" :f"{int((distance/35)*60)} mins", "comfort":"High"},
          "InDrive Rickshaw" : {"price" :f"Rs.{int(distance*25)}-{int(distance*35)}" , "time" :  f"{int((distance/35)*60)} mins", "comfort":"High"},
          "Bykea" : {"price" :f"Rs.{int(distance*4)+30}-{int(distance*5)+30}" , "time" :  f"{int((distance/40)*60)} mins", "comfort":"High"},
          "Yango" : {"price" :f"Rs.{int(distance*25)}-{int(distance*35)}" , "time" :  f"{int((distance/35)*60)} mins", "comfort":"High"},
          "Metro":     {"price": "Rs 30",    "time":  f"{int((distance/25)*60)} mins", "comfort": "Medium"},
        }
       results=transports
    return render_template("index.html",results=results,start=start,destination=destination,distance=distance,duration=duration)
                              
def get_route_info(start, destination):
    #start coordinates
    try:
        response=requests.get(f'https://api.openrouteservice.org/geocode/search?api_key={API_KEY}&text={start} Lahore Pakistan&boundary.country=PAK&size=1')
        data=response.json()
        start_cords=data['features'][0]['geometry']['coordinates']
    #end coordinates
        response1=requests.get(f'https://api.openrouteservice.org/geocode/search?api_key={API_KEY}&text={destination} Lahore Pakistan&boundary.country=PAK&size=1')
        data1=response1.json() 
        dest_cords=data1['features'][0]['geometry']['coordinates']
    #call directions API with both coordinates
        raw_directions=requests.get(f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={API_KEY}&start={start_cords[0]},{start_cords[1]}&end={dest_cords[0]},{dest_cords[1]}')
        data=raw_directions.json()
        distance=data['features'][0]['properties']['segments'][0]['distance']
        distance_km=round(distance/1000,1)

    #print('Distance',distance_km,' km')
        duration=data['features'][0]['properties']['segments'][0]['duration']
        duration_min=int(duration/60)
    #print('Duration',duration_min,'minutes') 

        return distance_km,duration_min   
    except Exception as e:
       return None,None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
   

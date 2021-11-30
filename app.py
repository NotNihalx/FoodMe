import re
from flask import Flask, request, render_template, redirect, url_for, jsonify, flash
import datetime, os, random, requests
from yelpapi import YelpAPI
from flask_googlemaps import GoogleMaps, Map

#init yelp api

#yelp key
yelp_key = 'pWLFRJGIhT0GzVd_QuUlAj6WhYI1MQH4raO9u6_8VNN0C9YpAus_lq3B8HrrsRinGSdxBFt3pvjPuIoEVoj1hTuHhyDdApOZdRgkdcxNvzxSj4WyZXjqjztGO3AYYHYx'
google_maps_key = 'AIzaSyBBSt28jTrLVUwrYGpsLESpvxv7hk_Cpqs'

YelpAPI = YelpAPI(yelp_key, timeout_s = 3.0)

# Global var
restaurant_list = []

app = Flask(__name__)
app.secret_key = os.urandom(24)
GoogleMaps(app, key=google_maps_key)


def get_coordinates(API_KEY, address_text):
    response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json?address="
        + address_text
        + "&key="
        + API_KEY
    ).json()
    return response["results"][0]["geometry"]["location"]


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/search', methods = ['GET', 'POST'])

def search():

    if request.method == 'POST':
        loc = ''

        try:
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                response = requests.get('http://ip-api.com/json')
                
                json_reponse = response.json()
                loc = json_reponse['city']
                print(f"User's IP address: {json_reponse['query']}. (Not forwarded)")
                print(f"Location based on ip address: {loc}. (Not forwarded)")

            else:
                print(f"User's IP address: {request.environ['HTTP_X_FORWARDED_FOR']}. (Forwarded)")
                ip = request.environ['HTTP_X_FORWARDED_FOR']
                response = requests.get(f"http://ip-api.com/json/{ip}")
                json_reponse = response.json()
                loc = json_reponse['city']
                print(f"Location based on ip address: {loc}. (Forwarded)")

        except:
            pass

        if request.form['button'] == 'Search using my location!':
            cuisine = request.form.get('cuisine')
        
        else:
            cuisine = request.form.get('cuisine')
            loc = request.form.get('loc')

            if request.form.get('loc') == '':
                flash("Enter your location")
                return render_template('search.html')
            
            else:
                pass
            
        result = YelpAPI.search_query(term = cuisine, location = loc, radius = 16000)
        restaurant_info = result['businesses']

        for restaurant in restaurant_info:

            new_restaurant = {}
            new_restaurant['name'] = restaurant['name']
            try:
                new_restaurant['price'] = restaurant['price']
            except:
                new_restaurant['price'] = 'N/A'
            new_restaurant['image'] = restaurant['image_url']
            new_restaurant['address'] = f"{restaurant['location']['display_address'][0]} {restaurant['location']['display_address'][1]}"
            new_restaurant['rating'] = restaurant['rating']
            new_restaurant['user_entered_type'] = cuisine
            new_restaurant['user_entered_location'] = loc
            
            restaurant_list.append(new_restaurant)

        return redirect(url_for('results'))

    else:
        return render_template('search.html')



@app.route('/results', methods = ['GET', 'POST'])

def results():

    if request.method == 'Post':
        # add feature to reset
        pass

    else:

        option1 = ''
        option2 = ''
        option3 = ''

        try:
            option1 = restaurant_list[random.randint(0, len(restaurant_list) - 1)]
            restaurant_list.remove(option1)
            option2 = restaurant_list[random.randint(0, len(restaurant_list) - 1)]
            restaurant_list.remove(option2)
            option3 = restaurant_list[random.randint(0, len(restaurant_list) - 1)]
            restaurant_list.remove(option3)
                
        except:
            flash("We could not find any restaruants for your cuisine type and/or location within 10 miles. Please try again!")
            print("Database empty")
            return render_template('search.html')

        restaurant_coordinates1 = get_coordinates(google_maps_key, f"{option1['address']} {option1['user_entered_location']}")
        restaurant_coordinates2 = get_coordinates(google_maps_key, f"{option2['address']} {option1['user_entered_location']}")
        restaurant_coordinates3 = get_coordinates(google_maps_key, f"{option3['address']} {option1['user_entered_location']}")

        coordinates = [
            {'latitude' : restaurant_coordinates1['lat'], 'longitude': restaurant_coordinates1['lng']},
            {'latitude' : restaurant_coordinates2['lat'], 'longitude': restaurant_coordinates2['lng']},
            {'latitude' : restaurant_coordinates3['lat'], 'longitude': restaurant_coordinates3['lng']},    
        ]

        testMap = Map(
            identifier='testmap',
            lat=coordinates[0]['latitude'],
            lng=coordinates[0]['longitude'],
            markers = [(loc['latitude'], loc['longitude']) for loc in coordinates],
            fit_markers_to_bounds = True,
            style = 'width:900px;height:400px'
        )

        context = {
            # Map

            'mymap' : testMap,

            # Option 1
            'name': option1['name'],
            'price': option1['price'],
            'rating': option1['rating'],
            'address': option1['address'],
            'image': option1['image'],
            'restaurant_type': option1['user_entered_type'],
            'restaurant_location': option1['user_entered_location'],
           
            # Option 2
            'name2': option2['name'],
            'price2': option2['price'],
            'rating2': option2['rating'],
            'address2': option2['address'],
            'image2': option2['image'],
            'restaurant_type': option1['user_entered_type'],
            'restaurant_location': option1['user_entered_location'],
          
            # Option 3
            'name3': option3['name'],
            'price3': option3['price'],
            'rating3': option3['rating'],
            'address3': option3['address'],
            'image3': option3['image'],
            'restaurant_type3': option3['user_entered_type'],
            'restaurant_location3': option3['user_entered_location'],
        }

        return render_template('results.html', **context)

if __name__ == '__main__':
    app.run()
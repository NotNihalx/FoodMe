from flask import Flask, request, render_template, redirect, url_for, jsonify, flash
import datetime, os, random, requests
from yelpapi import YelpAPI


app = Flask(__name__)

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
            
        result = YelpAPI.search_query(term = cuisine, location = loc)
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

        return redirect(url_for('results.html'))



    else:
        return render_template('search.html')

if __name__ == '__main__':
    app.run()
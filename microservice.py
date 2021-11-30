#Nihal's microservice

import requests

def get_loc():

    with open('ip.txt') as f:
        lines = f.read()

        ip = lines

    response = requests.get(f"http://ip-api.com/json/{ip}")

    json_reponse = response.json()
    loc = json_reponse['city']
    loc2 = json_reponse['regionName']
    loc3 = json_reponse['country']
    
    with open('loc.txt', 'w') as f:
        f.write(loc + '\n')
        f.write(loc2 + '\n')
        f.write(loc3)

get_loc()
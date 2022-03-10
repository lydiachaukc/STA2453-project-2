from urllib.request import urlopen
import json
with open('vaccine_data/Ministry_of_Health_Public_Health_Unit_Boundary.geojson') as response:
    counties = json.load(response)
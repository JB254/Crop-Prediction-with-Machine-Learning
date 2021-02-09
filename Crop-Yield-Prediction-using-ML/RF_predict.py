# import dependencies

import sys
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=UserWarning)
import pickle
import requests, json 

# print ('Number of arguments:', len(sys.argv), 'arguments.')
# print ('Argument List:', str(sys.argv))


# load trained model
with open('RF_Model', 'rb') as f:
    RanFor = pickle.load(f)

# set possible list values for region, crop and soil
dist_list = ['BARINGO', 'BOMET', 'BUNGOMA', 'BUSIA', 'EMBU', 'HOMA-BAY', 'ISIOLO', 'KAJIADO', 'KAKAMEGA', 'KERICHO', 'KIAMBU', 'KILIFI', 'KIRINYAGA', 'KISII', 'KISUMU', 'KITUI', 'KWALE', 'LAIKIPIA', 'LAMU', 'MACHAKOS', 'MAKUENI', 'MANDERA', 'MARSABIT', 'MERU', 'MIGORI', 'MOMBASA', 'MURANGA', 'NANDI', 'NYANDARUA', 'NYERI']
crop_list = ['Maize', 'Beans', 'Rice']
soil_list = ['alluvial', 'clay', 'loamy', 'sandy', 'silty']

# fetch district, crop, area and soil type from command line arguments
district = sys.argv[1]
Crop = sys.argv[2]
Area = int(sys.argv[3])
soil_type = sys.argv[4]


district = "District:_"+district
Crop = "Crop:_"+Crop
soil_type = "Soil_type:_"+soil_type


# set API key and base url to fetch real time data from OpenWeatherMap site

api_key = "fdb1847fbe28eb846a28e0b4bbcdf25a"
  
base_url = "http://api.openweathermap.org/data/2.5/weather?"

# set city for which weather data needs to be fetched

city_name = sys.argv[1]

complete_url = base_url + "appid=" + api_key + "&q=" + city_name 

# fetch data

response = requests.get(complete_url) 

x = response.json() 

# print(x)

# if response code is not 404 (not found), then proceed
if x["cod"] != "404": 
    y = x["main"] 
    temp = y["temp"]-273
    humi = y["humidity"]  
    try:
        preci_humi_link = 'https://www.worldweatheronline.com/bungoma-weather/western/ke.aspx'
        p2 = requests.get(preci_humi_link)
        s2 = BeautifulSoup(p2.content, 'html.parser')
        preci_table = ((s2.find_all('div', attrs={'class':'tb_cont_item', 'style':'background-color:#ffffff;'})))
        preci = 0
        for ele in preci_table[21::2]:
            if ele.text == '0.00 mm':
                preci += float(ele.text.replace("mm", "").strip())        
        preci *= 6
        # print("Average precipitation: ", preci)
        humi_table = ((s2.find_all('div', attrs={'class':'tb_row tb_rain'})))
        humi = 0
        for ele in humi_table:
            if len(ele.text) > 15:
                humi = ele.text.replace("Rain", "").split("%")[:-1]
        humi = sum(list(map(float, humi)))
        humi *= 6
        # print ("Average humidity: ", humi)
    except:
        preci = 0
        humi = 0

    # create input feature matrix

    X = ['Area', 'Temperature', 'Precipitaion', 'Humidity', 'Soil_type:_alluvial',
       'Soil_type:_clay', 'Soil_type:_loamy', 'Soil_type:_peaty',
       'Soil_type:_sandy', 'Soil_type:_silt', 'Soil_type:_silty',
       'District:_BARINGO', 'District:_BOMET', 'District:_BUNGOMA',
       'District:_BUSIA', 'District:_EMBU', 'District:_HOMA-BAY',
       'District:_ISIOLO', 'District:_KAJIADO', 'District:_KAKAMEGA',
       'District:_KERICHO', 'District:_KIAMBU', 'District:_KILIFI',
       'District:_KIRINYAGA', 'District:_KISII', 'District:_KISUMU',
       'District:_KITUI', 'District:_KWALE', 'District:_LAIKIPIA',
       'District:_LAMU', 'District:_MACHAKOS', 'District:_MAKUENI',
       'District:_MANDERA', 'District:_MARSABIT', 'District:_MERU',
       'District:_MIGORI', 'District:_MOMBASA', 'District:_MURANGA',
       'District:_NANDI', 'District:_NYANDARUA', 'District:_NYERI',
       'Crop:_Maize', 'Crop:_Beans', 'Crop:_Rice', 'Season:_Hot',
       'Season:_Wet', 'Season:_Cold       ']

    index_dict = dict(zip(X,range(len(X))))

    vect = {}
    for key, val in index_dict.items():
        vect[key] = 0

    # set values received from user into the input feature matrix

    try:
        vect[district] = 1
    except Exception as e:
        print("Exception occured for DISTRICT!", e)
    try:
        vect[Crop] = 1
    except Exception as e:
        print("Exception occured for CROP!")
    try:
        vect[soil_type] = 1
    except Exception as e:
        print("Exception occured for SOIL TYPE!")
    try:
        vect['Area'] = Area
    except Exception as e:
        print("Exception occured for AREA!", e)
    try:
        vect['Temperature'] = temp
    except Exception as e:
        print("Exception occured for TEMP!", e)
    try:
        vect['Precipitaion'] = preci
    except Exception as e:
        print("Exception occured for PRECI!", e)
    try:
        vect['Humidity'] = humi
    except Exception as e:
        print("Exception occured for HUMI!", e)

    now = datetime.datetime.today()
    season = "Season:_Hot" if (now.month >= 7 and now.month <= 10) else "Season:_Wet"
    vect[season] = 1

    # print(vect, len(vect))
    df = pd.DataFrame.from_records(vect, index=[0])

    # make predictions
    crop_yield = RanFor.predict(df)[0]
    print ("The predicted YIELD for given attributes is approximately: ", (crop_yield), "tons.")


else: 
    print(" District Not Found ")
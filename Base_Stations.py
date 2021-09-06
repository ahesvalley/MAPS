import requests
import os, zipfile, io

from selenium import webdriver
from tqdm import tqdm
import pandas as pd
import csv
import folium


ufr = requests.get('https://op.mos.ru/EHDWSREST/catalog/export/get?id=1056908')
pd.set_option( 'display.max_columns', 25)
with ufr, zipfile.ZipFile(io.BytesIO(ufr.content)) as archive:
    acnc = pd.read_excel(io.BytesIO(archive.read(archive.infolist()[0])), keep_default_na=False, engine='openpyxl')
print(acnc.head())
File = acnc[['NameOwner', 'Location', 'Longitude_WGS84', 'Latitude_WGS84']]
File['Url'] = ['https://www.google.com/maps/search/' + a for a in File['Location']]
print(File.head())

URL_FROM_REQUEST = []
if not os.path.isfile('URL_FROM_REQUEST.csv'):
    option = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'images': 2, 'javascript': 2}}
    option.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome("chromedriver.exe", options=option)

    for url in tqdm(File.Url, leave=False):
        driver.get(url)
        URL_FROM_REQUEST.append(driver.find_element_by_css_selector('meta[itemprop=image]').get_attribute('content'))
    driver.close()

    with open('URL_FROM_REQUEST.csv', 'w') as file:
        wr = csv.writer(file)
        wr.writerow(URL_FROM_REQUEST)
else:
    with open('URL_FROM_REQUEST.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for i in reader:
            URL_FROM_REQUEST = i
            break

File['URL_FROM_REQUEST'] = URL_FROM_REQUEST

print(URL_FROM_REQUEST)
File['lat'] = [ url.split('?center=')[1].split('&zoom=')[0].split('%2C')[0] for url in File['URL_FROM_REQUEST'] ]
File['long'] = [url.split('?center=')[1].split('&zoom=')[0].split('%2C')[1] for url in File['URL_FROM_REQUEST'] ]
map_coord = list(File[['lat', 'long']].astype(float).mean(axis=0))
melMap = folium.Map(map_coord)
DataMap = folium.Map(map_coord)

for lat, long, name, lat2, long2 in zip(File.lat, File.long, File.Name, File.Latitude_WGS84, File.Longitude_WGS84):
    folium.Marker([lat, long],
                  icon=folium.CustomIcon(icon_image='https://i.imgur.com/CYx04oC.png', icon_size=(10, 10)),
                  popup='Базовая станция: \n\n' + name + '\n\n').add_to(melMap)
melMap.save('Base_Station_map.html')

import requests
import os, zipfile, io

from selenium import webdriver
from tqdm import tqdm
import pandas as pd
import csv
import folium
import pathlib
import openpyxl
import numpy

def Polygon(polygon, melMap):
    longlist = []
    latlist = []
    b = polygon
    b = b.split(',')
    for l in range(0, len(b), 2):
        rem = b[l].replace('[', '')
        rem = rem.replace(']', '')
        longlist.append(rem)
    for l in range(1, len(b), 2):
        rem = b[l].replace('[', '')
        rem = rem.replace(']', '')
        latlist.append(rem)
    polygonList = []
    for n in range(0, len(latlist)):
        polygonListCoord = []
        polygonListCoord.append(float(latlist[n]))
        polygonListCoord.append(float(longlist[n]))
        polygonList.append(list(polygonListCoord))

    folium.Polygon([polygonList], color="blue", weight=1, opacity=1, fill_color='blue').add_to(melMap)

#work_path = pathlib.Path.cwd()
#print(work_path)
#acnc_path = (str(work_path)+'\data-6486-2021-02-10.zip')
pd.set_option( 'display.max_columns', 25)
acnc = pd.read_excel(r'data-6486-2021-02-10.xlsx')
#print(acnc.head())
acnc = acnc[['Name', 'Location', 'YearOfComissioning', 'geoData']]
acnc['polygon'] =[ poly.split('coordinates=[')[1].split('], center=')[0] for poly in acnc['geoData'] ]
acnc['center'] = [centr.split('], center=[')[1].split(']}')[0] for centr in acnc['geoData']]
acnc['long'] = [lat.split('[')[1].split(', ')[0] for lat in acnc['center']]
acnc['lat'] = [long.split(', ')[1].split(']')[0] for long in acnc['center']]
a = acnc['polygon'].values


map_coord = list(acnc[['lat', 'long']].astype(float).mean(axis=0))

melMap = folium.Map(map_coord)

DataMap = folium.Map(map_coord)

for lat, long, name, year, polygon in zip(acnc.lat, acnc.long, acnc.Name, acnc.YearOfComissioning, a):

    folium.Marker([lat, long],
                  icon=folium.CustomIcon(icon_image='https://img.pngio.com/geolocation-icon-png-393180-free-icons-library-png-market-map-1024_1024.jpg', icon_size=(10, 10)),
                  tooltip='Мост Москвы: \n\n' + name + '\n\n' + str(year)).add_to(melMap)

    Polygon(polygon, melMap)

melMap.save('Bridge_map.html')


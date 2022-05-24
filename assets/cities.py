import csv
from collections import defaultdict
from typing import DefaultDict, List
import logging

zip_mapping: DefaultDict[str, List[str]] = defaultdict(lambda: [])
city_mapping: DefaultDict[str, List[str]] = defaultdict(lambda: [])

path = 'assets/data/zip_cities_sample.csv'

with open(path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        
        for row in reader:
            
            zip_code = row[0]
            city = row[1]
            

            if '-' in city:
                zip_mapping[zip_code].append(city.replace('-', ' '))
                city_mapping[city.replace('-', ' ')].append(zip_code)

            zip_mapping[zip_code].append(city)
            city_mapping[city].append(zip_code)
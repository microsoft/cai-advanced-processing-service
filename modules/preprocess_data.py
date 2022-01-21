import aiohttp
import asyncio
import datetime
import re
from typing import List, Dict, Tuple, Union, Any

from modules import process_input

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

def get_entities(r_pred: JSONType) -> JSONType:
    try:
        entities:JSONType = r_pred.get('entities')
    except IndexError:
        entities = None
    except KeyError:
        entities = None

    return entities


def get_street(query: str, r_pred: JSONType) -> Tuple[Union[str, None], Union[str, None], Union[str, None], Union[str, None]]:
    """Orchestrate street name and number formatting and validation"""

    if r_pred is not None:
        entities = get_entities(r_pred)
    else:
        entities = None
    if entities is None or len(entities) == 0:
        l_street = None
        l_number = None
    else:
        try:
            entities = entities.get('Strasse+Nr')[0]
            l_street: Union[str, None] = entities.get('Strasse')[0]
            l_number: Union[str, None] = entities.get('Hausnummer')[0]
        except IndexError:
            l_street = None
            l_number = None
        except KeyError:
            l_street = None
            l_number = None

    # luis could not get entities
    if l_street is None or l_number is None:
        s_name, s_number = inputprocessing.split_numbers_pos(query)
    else:
        s_name = l_street
        s_number = l_number

    s_name = inputprocessing.pp_normalize_street_name(s_name)
    l_street = inputprocessing.pp_normalize_street_name(l_street)

    return s_name, s_number, l_street, l_number


def get_zip_city(query: str, r_pred: JSONType) -> Tuple[Union[str, None], Union[str, None], Union[str, None], Union[str, None]]:
    """Orchestrate street name and number formatting and validation"""

    if r_pred is not None:
        entities = get_entities(r_pred)
    else:
        entities = None
    l_zip: Union[str, None] = None
    l_city: Union[str, None] = None
    if entities is not None:

        try:
            entities: JSONType = entities.get('PLZ+Ort')

            for e in entities:
                if 'PLZ' in e:
                    l_zip = e['PLZ'][0]
                if 'Ort' in e:
                    l_city = e['Ort'][0]

        except IndexError:
            l_zip = None
            l_city = None
        except KeyError:
            l_zip = None
            l_city = None
        except TypeError:
            l_zip = None
            l_city = None

        s_city, s_zip = inputprocessing.split_numbers_naive(query)

        # luis has the zip code. In this case take the zip code that luis generated
        if l_zip is not None:
            s_zip = l_zip

        # map city based on zip code
        s_city = inputprocessing.match_zip_to_city(s_zip, s_city, 0.1)
    
    else:
        s_city, s_zip = inputprocessing.split_numbers_naive(query)
        s_city = inputprocessing.match_zip_to_city(s_zip, s_city, 0.7)


    return s_zip, s_city, l_zip, l_city


def get_dob(query: str, r_pred: JSONType) -> Tuple[str, Union[str, None]]:
    """Orchestrate street name and number formatting and validation"""

    if r_pred is not None:
        entities = get_entities(r_pred)
    else:
        entities = None
    l_dob = 'XXXX-XX-XX'
    s_dob = None
    l_dob_past = 'XXXX-XX-XX'
    if entities is not None:

        try:
            for e in entities.keys():
                if e == 'dob':
                    s_dob: Union[str, None] = entities[e][0]
                
                elif e == 'datetimeV2':
                    l_dob: Union[str, None] = entities[e][0]['values'][0]['timex']

                elif e == 'datePast':
                    l_dob_past = parse_date_past(entities)


        except IndexError:
            l_dob = None
        except KeyError:
            l_dob = None

    # use datePast entity type if datetimeV2 contains unknowns (datePast is more robust)
    if 'X' in l_dob and not 'X' in l_dob_past:
        return l_dob_past, s_dob

    if l_dob is None:
        l_dob = 'XXXX-XX-XX'

    s_dob, l_dob = checkCenturyAnomaly(s_dob, l_dob)

    return l_dob, s_dob

def checkCenturyAnomaly(s_dob: str, l_dob: str):
    try:
        dateSplitted = s_dob.split(' ')
    
        day = dateSplitted[0].zfill(2)
        month = dateSplitted[1].zfill(2)
        yearSplitted = dateSplitted[2:]

        if len(dateSplitted)==5:
            if yearSplitted[0]=='9' and yearSplitted[1]=='10':
                year = '19' + yearSplitted[2][-2:]
            if yearSplitted[0]=='19' and yearSplitted[1]=='100':
                year = '19' + yearSplitted[2][-2:]

        if len(dateSplitted)==4:
            if yearSplitted[0]=='9' and yearSplitted[1].startswith('10'):
                year = '19' + yearSplitted[1][-2:]            

        if year:
            return day + ' ' + month + ' ' + year, year + '-' + month + '-' + day
    except:
        return s_dob, l_dob
    
    return s_dob, l_dob

def parse_date_past(date_past_entity: JSONType) -> str:
    day: Union[str, None] = 'XX'
    month: Union[str, None] = 'XX'
    year: Union[str, None] = 'XXXX'

    for key in date_past_entity.keys():
        if key == 'datePast':
            for e in date_past_entity[key]:
    
                if 'day_month' in e:
                    day_month = e['day_month'][0]
                    if len(day_month) == 4:
                        day = e['day_month'][0][:2]
                        month = e['day_month'][0][2:]
                
                elif 'day' in e:
                    day: Union[str, None] = e['day'][0]
                    day = inputprocessing.prepend_chars(day, 2, '0')
                    if day is not None:
                        day = inputprocessing.reduce_ordinals(day, strip=True)

                elif 'month' in e:
                    month = e['month'][0]
                    month = inputprocessing.prepend_chars(month, 2, '0')
                    if month is not None:
                        month = inputprocessing.reduce_months(month, strip=True)

                
                        
                elif 'year' in e:
                    year = e['year'][0]

                    if year is None:
                        continue

                    # extract patterns like 910 183 -> 1983
                    if '910' in year:
                        # usually the last two digits correspond to the year
                        year = '19' + year[-2:]

                    if len(year) == 2:                
                        current_year = datetime.datetime.now().year
                        # assume that current year - 18 means 20XX (e.g. 01 means 2001)
                        if int(year) >= (current_year - 2018):
                            year = '19' + year
                        else:
                            year = '20' + year
    return f'{year}-{month}-{day}'
    

def get_iban(query: str, r_pred: str) -> str:

    # remove characters and whitespaces
    pp_iban = inputprocessing.pp_remove_chars(query)
    pp_iban = re.sub(r'(\d)\s+(\d)', r'\1\2', pp_iban)

    # return last 5 digits
    return pp_iban[-5:]

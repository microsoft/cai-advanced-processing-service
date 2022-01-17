import sys
import configparser
import json
import logging
import os
import asyncio
import azure.functions as func
import pandas as pd

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from azure.cosmosdb.table.tablebatch import TableBatch

try:
    from __app__.shared import Logging as log
    from __app__.shared import Preprocessing as preprocessing
    from __app__.shared import InputProcessing as inputprocessing
    from __app__.shared import Validation as validation
except Exception as e:
    from shared import Logging as log
    from shared import Preprocessing as preprocessing
    from shared import InputProcessing as inputprocessing
    from shared import Validation as validation

from typing import Union

# Load keys
luis_id = os.environ.get('LUIS_ID')
luis_key = os.environ.get('LUIS_KEY')
luis_location = os.environ.get('LUIS_LOCATION')
sa_connection_string = os.environ.get("WEBSITE_CONTENTAZUREFILECONNECTIONSTRING")

if luis_key is None:
    # Local debugging
    sys.path.append('./')
    config = configparser.ConfigParser()
    config.read('config.ini')
    luis_id = config['luis']['appid']
    luis_key = config['luis']['key']
    luis_location = config['luis']['location']
    sa_connection_string = config['general']['sa_connection_string']

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:

    user_input = req.params.get('userInput')
    user_zip = req.params.get('zip')
    user_city = req.params.get('city')
    user_street = req.params.get('street') # mandatory
    user_number = req.params.get('number') # optional

    log.logger.info("[INFO] Validate Address... userInput: '{}' user_zip: '{}' user_city: '{}' user_street: '{}' user_number: '{}'".format(user_input, user_zip, user_city, user_street, user_number))

    city_name = None
    r_pred = None

    if (not user_zip is None and not user_city is None):
        log.logger.info(f"[INFO] Using ZIP and City from Request")
        zip_code = user_zip.replace(" ", "").zfill(5)
        log.logger.info(zip_code)
        city_name = inputprocessing.match_zip_to_city(zip_code, user_city, 0.1)

    if(not city_name and not user_input is None):
        log.logger.info(f"[INFO] No zip/city data: using userInput")

        r = await preprocessing.score_luis(context.invocation_id, False, user_input, luis_id, luis_key, luis_location)
        r_pred = r.get('prediction')

        zip_code, city_name, l_zip_code, l_city_name = preprocessing.get_zip_city(user_input, r_pred)

    if zip_code and city_name:
        if zip_code[0] == '0':
            zip_code = zip_code[1:]

        log.logger.info("[INFO] Found match for ZIP and City: {} {}".format(zip_code, city_name))   
        status_code = 200

        # check street
        result = None
        try: 
            table_service = TableService(connection_string=sa_connection_string)
            tasks = table_service.query_entities('StreetsInZipLocation', filter="PartitionKey eq '" + str(zip_code) + "'", select='RowKey')
        except:
            res = json.dumps(dict(userInput = user_input, error = True, error_message = "Error accessing database / ZIP not found", city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
            return func.HttpResponse(res, mimetype='application/json', status_code=status_code)

        streetsInZipArea = [task.RowKey for task in tasks]
        if (not user_street is None):
            result = validation.get_matching_streets(user_street, streetsInZipArea)

        if not result and user_input:
            log.logger.info("[INFO] No street data from user_street '{}' in zip_code '{}': using userInput '{}' and LUIS".format(user_street, zip_code, user_input))
            # call luis if we haven't already
            if not r_pred:
                r = await preprocessing.score_luis(context.invocation_id, False, user_input, luis_id, luis_key, luis_location)
                r_pred = r.get('prediction')
            try:
                street_name, street_number, l_street, l_number = preprocessing.get_street(user_input, r_pred) 
                if street_name[-3:] == "str":
                    street_name = street_name[:-3] + "straße" 
                log.logger.info("[INFO] LUIS answer... street_name: {},  street_number: {} ".format(street_name, street_number))

                result = validation.get_matching_streets(street_name, streetsInZipArea)
                user_number = street_number
            except:
                log.logger.warning("[WARNING] LUIS error. ")

        if not result:
            # no matches for street found
            res = json.dumps(dict(userInput = user_input, error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
        elif len(result) > 3:
            # to many matches for street found
            res = json.dumps(dict(userInput = user_input, error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = True))
        elif len(result) > 1:
            # multiple matches for street found
            res = json.dumps(dict(userInput = user_input, error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = True, streets = result, number = user_number))
        else:
            # one street found
            res = json.dumps(dict(userInput = user_input, error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = False, street = result[0], number = user_number))
    else: 
        log.logger.info(f"[INFO] No match found for ZIP and City")
        res = json.dumps(dict(error = False, city_is_valid = False, street_is_valid = False, street_has_options = False)) 

    return func.HttpResponse(res, mimetype='application/json')

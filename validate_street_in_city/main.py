import sys
import configparser
import json
import os
import asyncio
import azure.functions as func

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from azure.cosmosdb.table.tablebatch import TableBatch

try:
    from __app__.shared import Logging as log
    from __app__.shared import Preprocessing as preprocessing
    from __app__.shared import Validation as validation
except Exception as e:
    from shared import Logging as log
    from shared import Preprocessing as preprocessing
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
    # Input would be full user input and zip for city 
    try:
        user_input = req.params.get('userInput')
        user_street = req.params.get('street') # mandatory
        user_number = req.params.get('number') # optional
        user_zip = req.params.get('zip') # mandatory
    except ValueError as e:
        user_input = None
        user_street = None
        user_zip = None
        log.logger.exception(f"[INFO] Value error getting body values")

    log.logger.info("[INFO] Validate Street... userInput: '{}' user_zip '{}': user_street: '{}' user_zip '{}'".format(user_input, user_street, user_number, user_zip))

    status_code = 400
    res = json.dumps(dict(error = True, error_message = "Input error", is_valid = False, has_options = False))

    if (not user_street is None and not user_zip is None):

        if user_zip[0] == '0':
            user_zip = user_zip[1:]

        try: 
            table_service = TableService(connection_string=sa_connection_string)
            tasks = table_service.query_entities('StreetsInZipLocation', filter="PartitionKey eq '" + str(user_zip) + "'", select='RowKey')
        except:
            res = json.dumps(dict(userInput = user_input, error = True, error_message = "Error accessing database / ZIP not found", is_valid = False, has_options = False))
            return func.HttpResponse(res, mimetype='application/json', status_code=status_code)

        streetsInZipArea = [task.RowKey for task in tasks]

        result = validation.get_matching_streets(user_street, streetsInZipArea)

        if not result and user_input:
            log.logger.info("[INFO] No street data from user_street '{}' in user_zip '{}': using userInput '{}' and LUIS".format(user_street, user_zip, user_input))
            # call luis
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

        status_code = 200
        if not result:
            # no matches for street found
            res = json.dumps(dict(userInput = user_input, error = False, is_valid = False, has_options = False))
        elif len(result) > 3:
            # to many matches for street found
            res = json.dumps(dict(userInput = user_input, error = False, is_valid = False, has_options = True))
        elif len(result) > 1:
           # multiple matches for street found
            res = json.dumps(dict(userInput = user_input, error = False, is_valid = True, has_options = True, streets = result, number = user_number))
        else:
            # one street found
            res = json.dumps(dict(userInput = user_input, error = False, is_valid = True, has_options = False, street = result[0], number = user_number))

    return func.HttpResponse(res, mimetype='application/json', status_code=status_code)

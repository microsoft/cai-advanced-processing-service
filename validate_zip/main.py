import sys
import configparser
import json
import logging
import os
import asyncio
import azure.functions as func
import pandas as pd

try:
    from __app__.shared import Logging as log
    from __app__.shared import Preprocessing as preprocessing
    from __app__.shared import InputProcessing as inputprocessing
except Exception as e:
    from shared import Logging as log
    from shared import Preprocessing as preprocessing
    from shared import InputProcessing as inputprocessing

from typing import Union

# Load keys
luis_id = os.environ.get('LUIS_ID')
luis_key = os.environ.get('LUIS_KEY')
luis_location = os.environ.get('LUIS_LOCATION')

if luis_key is None:
    # Local debugging
    sys.path.append('./')
    config = configparser.ConfigParser()
    config.read('config.ini')
    luis_id = config['luis']['appid']
    luis_key = config['luis']['key']
    luis_location = config['luis']['location']

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:

    user_input = req.params.get('userInput')
    user_zip = req.params.get('zip')
    user_city = req.params.get('city')

    log.logger.info("[INFO] Validate ZIP... userInput: '{}' user_zip: '{}' user_city: '{}' ".format(user_input, user_zip, user_city))

    city_name = None

    if (not user_zip is None and not user_city is None):
        
        log.logger.info(f"[INFO] Using ZIP and City from Request")
        zip_code = user_zip.zfill(5)
        log.logger.info(zip_code)
        city_name = inputprocessing.match_zip_to_city(zip_code, user_city, 0.1)

    if(not city_name and not user_input is None):

        log.logger.info(f"[INFO] No street data: using userInput")

        r = await preprocessing.score_luis(context.invocation_id, False, user_input, luis_id, luis_key, luis_location)
        r_pred = r.get('prediction')

        zip_code, city_name, l_zip_code, l_city_name = preprocessing.get_zip_city(user_input, r_pred)

    if zip_code and city_name:
        log.logger.info("[INFO] Found match for ZIP and City: {} {}".format(zip_code, city_name))
        res = json.dumps(dict(error = False, is_valid = True, zip = zip_code, city = city_name))
    else: 
        log.logger.info(f"[INFO] No match found for ZIP and City")
        res = json.dumps(dict(error = False,is_valid = False, has_options = False)) 

    return func.HttpResponse(res, mimetype='application/json')

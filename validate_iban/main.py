import sys
import configparser
import json
import os
import asyncio
import azure.functions as func
import string
from typing import Union

try:
    from __app__.shared import Logging as log
    from __app__.shared import InputProcessing as inputprocessing
except Exception as e:
    from shared import Logging as log
    from shared import InputProcessing as inputprocessing

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:

    try:
        user_input = req.params.get('userInput') # Not used at the moment
        user_iban = req.params.get('iban')        
    except ValueError as e:
        user_input = None
        user_iban = None
        log.logger.exception("[INFO] Value error getting GET parameters values")

    log.logger.info("[INFO] Validate IBAN... userInput: '{}' user_iban: '{}' ".format(user_input, user_iban))
  
    if (not user_input is None and not user_iban is None):
        status_code = 200

        reduced_iban = inputprocessing.reduce_query(user_iban)      
        reduced_iban = reduced_iban.replace(' ','')

        log.logger.info("IBAN after preprocessing: {}".format(reduced_iban))

        if(len(reduced_iban) != 22 or not reduced_iban.startswith('DE')): # German IBAN -> 22 chars
            log.logger.info("IBAN is not a valid German IBAN")
            res = json.dumps(dict(error = False, error_message = "IBAN is not a valid German IBAN starting with 'DE' and length of 22", is_valid = False))
            return func.HttpResponse(res, mimetype='application/json', status_code=status_code)
        
        # translation map
        LETTERS = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}

        # move first 4 characters to the end and map letters to numbers
        valNumber = (reduced_iban[4:] + reduced_iban[:4]).translate(LETTERS)

        if (int(valNumber)%97)==1:
            res = json.dumps(dict(error = False, is_valid = True, iban = reduced_iban))                    
        else:
            # ToDo: Implement validation logic using user input
            res = json.dumps(dict(error = False, is_valid = False))    
    else:
        status_code = 400        
        res = json.dumps(dict(error = True, error_message = "Missing input parameter. Please provide the parameters iban and userInput", is_valid = False))

    return func.HttpResponse(res, mimetype='application/json', status_code=status_code)

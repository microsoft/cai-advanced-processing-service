import os
import azure.functions as func
import logging
import json
import string
from azure.cosmosdb.table.tableservice import TableService

try:
    from __app__.modules import preprocess_data
    from __app__.modules import process_input
    from __app__.modules import validate_data
except Exception as e:
    from modules import preprocess_data
    from modules import process_input
    from modules import validate_data

# Define logger
logger = logging.getLogger(__name__)

class Validator(object):
    def __init__(self, module, region="de"):
        # Set module vor validation
        if module == "iban":
            self.matcher = self.ValidateIBAN()
            self.luis_connection = False
        elif module == "address":
            self.matcher = self.ValidateAddress()
            self.luis_connection = get_luis_creds(region)
        elif module == "street_in_city":
            self.matcher = self.ValidateStreet()
            self.luis_connection = False
        elif module == "zip":
            self.matcher = self.ValidateZIP()
            self.luis_connection = False
        else:
            self.matcher = None
            self.luis_connection = False
    
    class ValidateIBAN(object):
        def __init__(self, body):
            self.body = body
            return None

        def run(self):
            reduced_iban = process_input.reduce_query(self.user_iban)      
            reduced_iban = reduced_iban.replace(' ','')
            
            if(len(reduced_iban) != 22 or not reduced_iban.startswith('DE')): # German IBAN -> 22 chars
                logging.info("IBAN is not a valid German IBAN")
                res = json.dumps(dict(error = False, error_message = "IBAN is not a valid German IBAN starting with 'DE' and length of 22", is_valid = False))
                return func.HttpResponse(res, mimetype='application/json', status_code=200)
            
            # translation map
            LETTERS = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}

            # move first 4 characters to the end and map letters to numbers
            validation_number = (reduced_iban[4:] + reduced_iban[:4]).translate(LETTERS)

            if (int(validation_number)%97)==1:
                res = json.dumps(dict(error = False, is_valid = True, iban = reduced_iban))                    
            else:
                # ToDo: Implement validation logic using user input
                res = json.dumps(dict(error = False, is_valid = False)) 
            return res

    class ValidateAddress(object):
        def __init__(self):
            return None

        def run(self):
            logging.info("[INFO] Validate Address... userInput: '{}' user_zip: '{}' user_city: '{}' user_street: '{}' user_number: '{}'".format(user_input, user_zip, user_city, user_street, user_number))

            city_name = None
            r_pred = None

            if (not user_zip is None and not user_city is None):
                logging.info(f"[INFO] Using ZIP and City from Request")
                zip_code = user_zip.replace(" ", "").zfill(5)
                logging.info(zip_code)
                city_name = process_input.match_zip_to_city(zip_code, user_city, 0.1)

            if(not city_name and not user_input is None):
                logging.info(f"[INFO] No zip/city data: using userInput")

                r = preprocess_data.score_luis(context.invocation_id, False, user_input, luis_id, luis_key, luis_location)
                r_pred = r.get('prediction')

                zip_code, city_name, l_zip_code, l_city_name = preprocess_data.get_zip_city(user_input, r_pred)

            if zip_code and city_name:
                if zip_code[0] == '0':
                    zip_code = zip_code[1:]

                logging.info("[INFO] Found match for ZIP and City: {} {}".format(zip_code, city_name))   
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
                    result = validate_data.get_matching_streets(user_street, streetsInZipArea)

                if not result and user_input:
                    logging.info("[INFO] No street data from user_street '{}' in zip_code '{}': using userInput '{}' and LUIS".format(user_street, zip_code, user_input))
                    # call luis if we haven't already
                    if not r_pred:
                        r = preprocess_data.score_luis(context.invocation_id, False, user_input, luis_id, luis_key, luis_location)
                        r_pred = r.get('prediction')
                    try:
                        street_name, street_number, l_street, l_number = preprocessing.get_street(user_input, r_pred) 
                        if street_name[-3:] == "str":
                            street_name = street_name[:-3] + "straße" 
                        logging.info("[INFO] LUIS answer... street_name: {},  street_number: {} ".format(street_name, street_number))

                        result = validate_data.get_matching_streets(street_name, streetsInZipArea)
                        user_number = street_number
                    except:
                        logging.warning("[WARNING] LUIS error. ")

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
                logging.info(f"[INFO] No match found for ZIP and City")
                res = json.dumps(dict(error = False, city_is_valid = False, street_is_valid = False, street_has_options = False)) 
            return res

    class ValidateStreet(object):
        def __init__(self):
            return None

        def run(self):
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

                result = validate_data.get_matching_streets(user_street, streetsInZipArea)

                if not result and user_input:
                    logging.info("[INFO] No street data from user_street '{}' in user_zip '{}': using userInput '{}' and LUIS".format(user_street, user_zip, user_input))
                    # call luis
                    r = preprocess_data.score_luis(context.invocation_id, False, user_input, luis_id, luis_key, luis_location)
                    r_pred = r.get('prediction')
                    try:
                        street_name, street_number, l_street, l_number = preprocess_data.get_street(user_input, r_pred) 
                        if street_name[-3:] == "str":
                            street_name = street_name[:-3] + "straße" 
                        logging.info("[INFO] LUIS answer... street_name: {},  street_number: {} ".format(street_name, street_number))

                        result = validate_data.get_matching_streets(street_name, streetsInZipArea)
                        user_number = street_number
                    except:
                        logging.warning("[WARNING] LUIS error. ")

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

            return res

    class ValidateZIP(object):
        def __init__(self):
            return None

        def run(self):
            city_name = None

            if (not user_zip is None and not user_city is None):
                
                logging.info(f"[INFO] Using ZIP and City from Request")
                zip_code = user_zip.zfill(5)
                logging.info(zip_code)
                city_name = process_input.match_zip_to_city(zip_code, user_city, 0.1)

            if(not city_name and not user_input is None):

                logging.info(f"[INFO] No street data: using userInput")

                r = preprocess_data.score_luis(context.invocation_id, False, user_input, luis_id, luis_key, luis_location)
                r_pred = r.get('prediction')

                zip_code, city_name, l_zip_code, l_city_name = preprocess_data.get_zip_city(user_input, r_pred)

            if zip_code and city_name:
                logging.info("[INFO] Found match for ZIP and City: {} {}".format(zip_code, city_name))
                res = json.dumps(dict(error = False, is_valid = True, zip = zip_code, city = city_name))
            else: 
                logging.info(f"[INFO] No match found for ZIP and City")
                res = json.dumps(dict(error = False,is_valid = False, has_options = False)) 

            return res


def get_luis_creds(region):
    try:
        """Retrieve LUIS credentials from env variables or local config and return as dict"""
        luis_creds = dict()
        luis_creds['luis_id'] = os.environ.get(f'LUIS_ID_{region}')
        luis_creds['luis_key'] = os.environ.get(f'LUIS_KEY_{region}')
        luis_creds['luis_prediction_endpoint'] = os.environ.get(f'LUIS_PREDICTION_ENDPOINT_{region}')
        luis_creds['luis_slot'] = os.environ.get(f'LUIS_SLOT_{region}')
        # Local debugging
        if luis_creds['luis_key'] is None:
            logger.info(f'[INFO] Entering local debugging')
            import sys
            sys.path.append('./')
            import configparser
            config = configparser.ConfigParser()
            config.read('config.ini')
            luis_creds['luis_id'] = config[f'luis_{region}']['appid']
            luis_creds['luis_key'] = config[f'luis_{region}']['key']
            luis_creds['luis_prediction_endpoint'] = config[f'luis_{region}']['prediction_endpoint']
            luis_creds['luis_slot'] = config[f'luis_{region}']['slot']
    except KeyError:
        logger.error(f'[ERROR] - No valid luis information found for this region -> {region}')
        luis_creds = None
    return luis_creds
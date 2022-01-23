'''HELPER FUNCTIONS AND BUSINESS LOGIC FOR ATTRIBUTE VALIDATOR'''
import logging
import json
import string
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService

# Import custom modules and helpers
from modules import preprocess_data, process_input, validate_data, request_table

# Define logger
logger = logging.getLogger(__name__)

class Validator(object):
    def __init__(self, module, values, manifest, region="de"):
        # Set values, region and manifest. Also, we gather connection data.
        # In case they cannot be retrieved (e.g. if not needed/available), they will be set to None
        self.values = values
        self.region = region.upper()
        self.manifest = manifest
        self.table_data = request_table.get_table_creds(['connection_string', ''])

        # Set module for validation
        if module == "iban":
            self.matcher = self.ValidateIBAN(self.values, self.region, self.manifest)
        elif module == "address":
            self.matcher = self.ValidateAddress(self.values, self.region, self.manifest, self.table_data)
        elif module == "street_in_city":
            self.matcher = self.ValidateStreet(self.values, self.region, self.manifest, self.table_data)
        elif module == "zip":
            self.matcher = self.ValidateZIP(self.values, self.region, self.manifest, self.table_data)
        else:
            self.matcher = False
        
        # Validate if we have all we need
        self.ready_to_run, self.message = self.check_parameters()

    def check_parameters(self):
        '''Verification if all required parameters are passed'''
        _required_parameters = {k for k, v in self.manifest['value_is_mandatory'].items() if v}
        # Check if request attributes in manifest
        if not set(self.values.keys()) <= set(self.manifest['value_is_mandatory'].keys()):
            return False, "received excess parameters"
        # Check if required attributes are there
        if not _required_parameters.issubset(set(self.values.keys())):
            return False, "required parameters are missing"
        return True, "success"
    
    class ValidateIBAN(object):
        def __init__(self, values, region, manifest, table_data):
            # Import from main class
            self.values = values
            self.region = region
            self.manifest = manifest
            self.table_data = table_data

        def run(self):
            reduced_iban = process_input.reduce_query(self.values["iban"].upper())      
            reduced_iban = reduced_iban.replace(' ','')
            logging.warning(self.manifest["locales"][self.region])
            
            if self.manifest['locales'][self.region]['length'] != len(reduced_iban) or not reduced_iban.startswith(self.region):
                logging.info(f"[INFO] - IBAN is not a valid IBAN for {self.region}")
                res = json.dumps(dict(error = False, error_message = f"Submitted IBAN is not a valid IBAN for {self.region} with length of {str(self.manifest['locales'][self.region]['length'])}", is_valid = False))
                return res
            
            # Translation map
            LETTERS = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}

            # Move first 4 characters to the end and map letters to numbers
            validation_number = (reduced_iban[4:] + reduced_iban[:4]).translate(LETTERS)

            # Check validity of IBAN validation number
            if (int(validation_number) % 97) == 1:
                res = json.dumps(dict(error = False, is_valid = True, iban = reduced_iban), default = str)                    
            else:
                # ToDo: Implement validation logic using user input
                res = json.dumps(dict(error = False, is_valid = False), default = str) 
            logging.warning(res)
            return res

    class ValidateAddress(object):
        def __init__(self, values, region, manifest, table_data):
            # Import from main class
            self.values = values
            self.region = region
            self.manifest = manifest
            self.table_data = table_data

        def run(self):
            city_name = None
            r_pred = None

            if (not self.values["zip"] is None and not self.values["city"] is None):
                logging.info(f"[INFO] - Using zip code and city from request")
                zip_code = self.values["zip"].replace(" ", "").zfill(5)
                city_name = process_input.match_zip_to_city(zip_code, self.values["city"], 0.1)

            if zip_code and city_name:
                if zip_code[0] == '0':
                    zip_code = zip_code[1:]
                logging.info('INFO] - Found match for zip/city')
                status_code = 200

                # Check street
                result = None
                try:
                    request_table.get_data_from_table(table_service['connection_data'])
                    tasks = table_service.query_entities('StreetsInZipLocation', filter="PartitionKey eq '" + str(zip_code) + "'", select='RowKey')
                except:
                    res = json.dumps(dict(userInput = self.values["input"], error = True, error_message = "Error accessing database / ZIP not found", city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
                    return func.HttpResponse(res, mimetype='application/json', status_code=status_code)

                _streets_in_zip_area = [task.RowKey for task in tasks]
                if (not self.values["street"] is None):
                    result = validate_data.get_matching_streets(self.values["street"], _streets_in_zip_area)

                if not result:
                    # no matches for street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
                elif len(result) > 3:
                    # to many matches for street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = True))
                elif len(result) > 1:
                    # multiple matches for street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = True, streets = result, number = user_number))
                else:
                    # one street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = False, street = result[0], number = user_number))
            else: 
                logging.info(f"[INFO] No match found for ZIP and City")
                res = json.dumps(dict(error = False, city_is_valid = False, street_is_valid = False, street_has_options = False)) 
            return res

    class ValidateStreet(object):
        def __init__(self, values, region, manifest, table_data):
            # Import from main class
            self.values = values
            self.region = region
            self.manifest = manifest
            self.table_data = table_data

        def run(self):
            status_code = 400
            res = json.dumps(dict(error = True, error_message = "Input error", is_valid = False, has_options = False))

            if (not self.values["street"] is None and not self.values["zip"] is None):

                if self.values["zip"][0] == '0':
                    user_zip = self.values["zip"][1:]

                try: 
                    table_service = TableService(connection_string=sa_connection_string)
                    tasks = table_service.query_entities('StreetsInZipLocation', filter=f"PartitionKey eq '{str(user_zip)}'", select='RowKey')
                except:
                    res = json.dumps(dict(userInput = self.values["input"], error = True, error_message = "Error accessing database / ZIP not found", is_valid = False, has_options = False))
                    return func.HttpResponse(res, mimetype='application/json', status_code=status_code)

                _streets_in_zip_area = [task.RowKey for task in tasks]

                result = validate_data.get_matching_streets(self.values["street"], _streets_in_zip_area)

                if not result:
                    # No matches for street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, is_valid = False, has_options = False))
                elif len(result) > 3:
                    # Too many matches for street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, is_valid = False, has_options = True))
                elif len(result) > 1:
                    # Multiple matches for street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, is_valid = True, has_options = True, streets = result, number = user_number))
                else:
                    # One street found
                    res = json.dumps(dict(userInput = self.values["input"], error = False, is_valid = True, has_options = False, street = result[0], number = user_number))

            return res

    class ValidateZIP(object):
        def __init__(self, values, region, manifest, table_data):
            # Import from main class
            self.values = values
            self.region = region
            self.manifest = manifest
            self.table_data = table_data

        def run(self):
            # Preprocess data
            if all([self.values["zip"], self.values["city"]]):
                logging.info(f"[INFO] - Using ZIP and City from Request")
                zip_code = self.values["zip"].zfill(5)
                city_name = process_input.match_zip_to_city(zip_code, self.values["city"], 0.1)
            else:
                city_name = None

            # Return values depending on match            
            if zip_code and city_name:
                logging.info("[INFO] - Found match for zip and city")
                res = json.dumps(dict(error = False, is_valid = True, zip = zip_code, city = city_name))
            else: 
                logging.info(f"[INFO] - No match found for zip and city")
                res = json.dumps(dict(error = False, is_valid = False, has_options = False)) 
            return res
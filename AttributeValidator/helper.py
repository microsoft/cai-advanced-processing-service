'''HELPER FUNCTIONS AND BUSINESS LOGIC FOR ATTRIBUTE VALIDATOR'''
import logging
import json
import string
import azure.functions as func

# Import custom modules and helpers
from modules import data_connector, process_input, validate_data
from assets.constants import (
    ADDRESS, 
    ATTRIBUTE_VALIDATOR_ENV,
    ATTRIBUTE_VALIDATOR_CITY_TABLE,
    ATTRIBUTE_VALIDATOR_ADDRESS_TABLE,
    CITY, 
    CONFIG, 
    HOUSE_NUMBER, 
    IBAN, 
    LOCAL_DATA_PATH, 
    LOCALES, 
    MODULES, 
    STREET, 
    STREET_IN_CITY, 
    USE_DB, 
    ZIP
)

# Define logger
logger = logging.getLogger(__name__)

class Validator(object):
    def __init__(self, module, manifest, values, region="de"):
        # Set values, region and manifest. Also, we gather connection data.
        # In case they cannot be retrieved (e.g. if not needed/available), they will be set to None
        self.module = module
        self.manifest = manifest[MODULES][self.module]
        self.config = manifest[CONFIG]
        self.values = values
        self.region = region.upper()
        if self.config[USE_DB]:
            self.table_connection_data = data_connector.get_table_creds(ATTRIBUTE_VALIDATOR_ENV)
        else:
            self.local_data_path = self.config[LOCAL_DATA_PATH]

        # Set module for validation
        if module == IBAN:
            self.matcher = self.ValidateIBAN(self.config, self.manifest, self.values, self.region)
        elif module == ADDRESS:
            self.matcher = self.ValidateAddress(self.config, self.manifest, self.values, self.region, self.table_connection_data)
        elif module == STREET_IN_CITY:
            self.matcher = self.ValidateStreet(self.config, self.manifest, self.values, self.region, self.table_connection_data)
        elif module == ZIP:
            self.matcher = self.ValidateZIP(self.config, self.manifest, self.values, self.region, self.table_connection_data)
        else:
            self.matcher = False
        
        # Validate if we have all needed parameters in the specified module
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
        def __init__(self, config, manifest, values, region):
            # Import from main class
            self.config = config
            self.manifest = manifest
            self.values = values
            self.region = region

        def run(self):
            reduced_iban = process_input.reduce_query(self.values[IBAN].upper())      
            reduced_iban = reduced_iban.replace(' ','')
            
            try:
                if self.manifest[LOCALES][self.region]['length'] != len(reduced_iban) or not reduced_iban.startswith(self.region):
                    logging.info(f"[INFO] - IBAN is not a valid IBAN for {self.region}")
                    res = json.dumps(dict(error = False, error_message = f"Submitted IBAN is not a valid IBAN for {self.region} with length of {str(self.manifest[LOCALES][self.region]['length'])}", is_valid = False))
                    return res
                
                # Translation map
                LETTERS = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}

                # Move first 4 characters to the end and map letters to numbers
                validation_number = (reduced_iban[4:] + reduced_iban[:4]).translate(LETTERS)

                # Check validity of IBAN validation number
                if (int(validation_number) % 97) == 1:
                    res = json.dumps(dict(error = False, is_valid = True, iban = reduced_iban), default = str)                    
                else:
                    # TODO: Implement validation logic using user input
                    res = json.dumps(dict(error = False, is_valid = False), default = str)
            except KeyError: # TODO: Throw error regarding invalid locale somewhere else
                res = json.dumps(dict(error = True, is_valid = False, error_message=f"Locale {self.region} not supported."), default = str)
            return res

    class ValidateAddress(object):
        def __init__(self, config, manifest, values, region, table_data):
            # Import from main class
            self.config = config
            self.manifest = manifest
            self.values = values
            self.region = region
            self.table_connection_data = table_data

        def run(self):
            logging.info(f"[INFO] - Using zip code and city from request")
            zip_code = self.values[ZIP].replace(" ", "").zfill(5)
            # Retrieve city names based on zip code
            try:
                tasks = data_connector.get_data_from_table(
                            self.table_connection_data, 
                            ATTRIBUTE_VALIDATOR_CITY_TABLE, 
                            ATTRIBUTE_VALIDATOR_ENV, 
                            {"PartitionKey": str(zip_code)}
                        )
            except Exception as e:
                logging.error(e)
            logging.warning(tasks)

            #city_name = process_input.match_zip_to_city(self.values[ZIP], self.values[CITY], 0.1)
            city_name = None
            if zip_code: #and city_name:
                if self.values[ZIP][0] == '0':
                    self.values[ZIP] = self.values[ZIP][1:]
                logging.info('INFO] - Found match for zip/city')

                # Check street
                result = None
                try:
                    tasks = data_connector.get_data_from_table(
                                self.table_connection_data, 
                                ATTRIBUTE_VALIDATOR_ADDRESS_TABLE, 
                                ATTRIBUTE_VALIDATOR_ENV, 
                                {"PartitionKey": str(zip_code)}
                            )
                except:
                    res = json.dumps(dict(error = True, error_message = "Error accessing database / ZIP not found", city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
                    return func.HttpResponse(res, mimetype='application/json', status_code=200)

                _streets_in_zip_area = [task.RowKey for task in tasks]
                if (not self.values[STREET] is None):
                    result = validate_data.get_matching_streets(self.values[STREET], _streets_in_zip_area)

                if not result:
                    # no matches for street found
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
                elif len(result) > 3:
                    # to many matches for street found
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = True))
                elif len(result) > 1:
                    # multiple matches for street found
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = True, streets = result, number = self.values.get(HOUSE_NUMBER)))
                else:
                    # one street found
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = False, street = result[0], number = self.values.get(HOUSE_NUMBER)))
            else: 
                logging.info(f"[INFO] No match found for ZIP and City")
                res = json.dumps(dict(error = False, city_is_valid = False, street_is_valid = False, street_has_options = False)) 
            return res

    class ValidateStreet(object):
        def __init__(self, config, manifest, values, region, table_data):
            # Import from main class
            self.config = config
            self.manifest = manifest
            self.values = values
            self.region = region
            self.table_connection_data = table_data

        def run(self):
            if self.values[ZIP][0] == '0':
                self.values[ZIP] = self.values[ZIP][1:]
            try: 
                tasks = data_connector.get_data_from_table(
                            self.table_connection_data, 
                            ATTRIBUTE_VALIDATOR_ADDRESS_TABLE, 
                            ATTRIBUTE_VALIDATOR_ENV, 
                            {"PartitionKey": str(self.values[ZIP])}
                        )
            except:
                res = json.dumps(dict(error = True, error_message = "Error accessing database / ZIP not found", is_valid = False, has_options = False))
                return func.HttpResponse(res, mimetype='application/json', status_code=400)

            _streets_in_zip_area = [task.RowKey for task in tasks]

            result = validate_data.get_matching_streets(self.values[STREET], _streets_in_zip_area)

            if not result:
                # No matches for street found
                res = json.dumps(dict(error = False, is_valid = False, has_options = False))
            elif len(result) > 3:
                # Too many matches for street found
                res = json.dumps(dict(error = False, is_valid = False, has_options = True))
            elif len(result) > 1:
                # Multiple matches for street found
                res = json.dumps(dict(error = False, is_valid = True, has_options = True, streets = result, number = self.values.get(HOUSE_NUMBER)))
            else:
                # One street found
                res = json.dumps(dict(error = False, is_valid = True, has_options = False, street = result[0], number = self.values.get(HOUSE_NUMBER)))
            return res

    class ValidateZIP(object):
        def __init__(self, config, manifest, values, region, table_data):
            # Import from main class
            self.config = config
            self.values = values
            self.region = region
            self.manifest = manifest
            self.table_connection_data = table_data

        def run(self):
            # Preprocess data
            if all([self.values[ZIP], self.values[CITY]]):
                logging.info(f"[INFO] - Using ZIP and City from request")
                zip_code = self.values[ZIP].zfill(5)
                city_name = process_input.match_zip_to_city(zip_code, self.values[CITY], 0.1)
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
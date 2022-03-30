'''HELPER FUNCTIONS AND BUSINESS LOGIC FOR ATTRIBUTE VALIDATOR'''
import logging
import json
import string
import azure.functions as func
from modules import luis_helper as luis
from modules import resolve_spelling as resolve
import re

# Import custom modules and helpers
from modules import process_input, validate_data
from modules.retrieve_credentials import CredentialRetriever
from modules.data_connector import DataConnector
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
    ATTRIBUTE_LOOKUP_STREET,
    ATTRIBUTE_LOOKUP_ZIP,
    USE_DB, 
    ZIP, 
    EMAIL
)

# Define logger
logger = logging.getLogger(__name__)

class Validator(object):
    def __init__(self, module, manifest, values, region="de", locale="de"):
        # Set values, region and manifest. Also, we gather connection data.
        # In case they cannot be retrieved (e.g. if not needed/available), they will be set to None
        self.module = module
        self.manifest = manifest[MODULES][self.module]
        self.config = manifest[CONFIG]
        self.values = values
        self.region = region.upper()
        self.locale = locale

        # Retrieve credentials and set up data connector
        self.credentials = CredentialRetriever(ATTRIBUTE_VALIDATOR_ENV,  normalize=('{region_code}', region)).load_credentials()
        self.connector = DataConnector(ATTRIBUTE_VALIDATOR_ENV, self.config, self.credentials).connector

        # Set module for validation
        if module == IBAN:
            self.matcher = self.ValidateIBAN(self.config, self.manifest, self.values, self.region)
        elif module == ADDRESS:
            self.matcher = self.ValidateAddress(self.config, self.manifest, self.values, self.region, self.connector)
        elif module == STREET_IN_CITY:
            self.matcher = self.ValidateStreet(self.config, self.manifest, self.values, self.region, self.connector)
        elif module == ZIP:
            self.matcher = self.ValidateZIP(self.config, self.manifest, self.values, self.region, self.connector)
        elif module == EMAIL:
            self.matcher = self.ValidateEMAIL(self.config, self.manifest, self.values, self.region, self.locale, self.connector)
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
        def __init__(self, config, manifest, values, region, connector):
            # Import from main class
            self.config = config
            self.manifest = manifest
            self.values = values
            self.region = region
            self.connector = connector

        def run(self):
            '''Run Validation for Address'''
            logging.info(f"[INFO] - Using zip code and city from request")
            zip_code = self.values[ZIP].replace(" ", "").zfill(5)
            # Retrieve city names based on zip code
            cities_matching_to_zip = self.connector.get_data(
                        ATTRIBUTE_VALIDATOR_CITY_TABLE, 
                        {"PartitionKey": ATTRIBUTE_LOOKUP_ZIP, ATTRIBUTE_LOOKUP_ZIP: str(zip_code)})
            zip_mapping, city_mapping = process_input.map_data_from_table(cities_matching_to_zip)

            # Match zip code to city names
            city_name = process_input.match_zip_to_city(self.values[ZIP], self.values[CITY], zip_mapping, 0.1)

            # If both zip code and city name were found, continue here
            if zip_code and city_name:
                # TODO: investigate why we check for a 0 here ...?
                if self.values[ZIP][0] == '0':
                    self.values[ZIP] = self.values[ZIP][1:]
                logging.info('INFO] - Found match for zip/city')

                # Check street - which streets are in this zip area?
                try:
                    streets_in_zip = self.connector.get_data(
                            ATTRIBUTE_VALIDATOR_ADDRESS_TABLE, 
                            {"PartitionKey": zip_code})
                except:
                    res = json.dumps(dict(error = True, error_message = "Error accessing database / ZIP not found", city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
                    return func.HttpResponse(res, mimetype='application/json', status_code=200)

                # Extract street names from result set
                street_name = [task[ATTRIBUTE_LOOKUP_STREET] for task in streets_in_zip]
                # Match streets - exact match or distance matching
                result = validate_data.get_matching_streets(self.values[STREET], street_name)

                # Found no matches to street
                if not result:
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = False))
                # Found too many matches for street
                elif len(result) > 3:
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = False, street_has_options = True))
                # Multiple matches for street
                elif len(result) > 1:
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = True, streets = result, number = self.values.get(HOUSE_NUMBER)))
                # Found one street
                else:
                    res = json.dumps(dict(error = False, city_is_valid = True, zip = zip_code.zfill(5), city = city_name, street_is_valid = True, street_has_options = False, street = result[0], number = self.values.get(HOUSE_NUMBER)))
            else: 
                logging.info(f"[INFO] No match found for ZIP and City")
                res = json.dumps(dict(error = False, city_is_valid = False, street_is_valid = False, street_has_options = False)) 
            return res

    class ValidateStreet(object):
        def __init__(self, config, manifest, values, region, connector):
            # Import from main class
            self.config = config
            self.manifest = manifest
            self.values = values
            self.region = region
            self.connector = connector

        def run(self):
            '''Run Validation for Street in ZIP'''
            if self.values[ZIP][0] == '0':
                self.values[ZIP] = self.values[ZIP][1:]

            # Check street - which streets are in this zip area?
            try: 
                streets_in_zip = self.connector.get_data(
                        ATTRIBUTE_VALIDATOR_ADDRESS_TABLE, 
                        {"PartitionKey": str(self.values[ZIP])})
            except:
                res = json.dumps(dict(error = True, error_message = "Error accessing database / ZIP not found", is_valid = False, has_options = False))
                return func.HttpResponse(res, mimetype='application/json', status_code=400)

             # Extract street names from result set
            street_name = [task[ATTRIBUTE_LOOKUP_STREET] for task in streets_in_zip]
            # Match streets - exact match or distance matching
            result = validate_data.get_matching_streets(self.values[STREET], street_name)

            # Found no matches to street
            if not result:
                res = json.dumps(dict(error = False, is_valid = False, has_options = False))
            # Found too many matches for street
            elif len(result) > 3:
                res = json.dumps(dict(error = False, is_valid = False, has_options = True))
            # Multiple matches for street
            elif len(result) > 1:
                res = json.dumps(dict(error = False, is_valid = True, has_options = True, streets = result, number = self.values.get(HOUSE_NUMBER)))
            # Found one street
            else:
                res = json.dumps(dict(error = False, is_valid = True, has_options = False, street = result[0], number = self.values.get(HOUSE_NUMBER)))
            return res

    class ValidateZIP(object):
        def __init__(self, config, manifest, values, region, connector):
            # Import from main class
            self.config = config
            self.values = values
            self.region = region
            self.manifest = manifest
            self.connector = connector

        def run(self):
            '''Run Validation for ZIP Codes'''
            # Preprocess data
            zip_code = self.values[ZIP].zfill(5)

            # Retrieve city names based on zip code
            cities_matching_to_zip = self.connector.get_data(
                        ATTRIBUTE_VALIDATOR_CITY_TABLE, 
                        {"PartitionKey": ATTRIBUTE_LOOKUP_ZIP, ATTRIBUTE_LOOKUP_ZIP: str(zip_code)})
            zip_mapping, city_mapping = process_input.map_data_from_table(cities_matching_to_zip)

            # Match zip code to city names
            city_name = process_input.match_zip_to_city(self.values[ZIP], self.values[CITY], zip_mapping, 0.1)

            # Return values depending on match            
            if zip_code and city_name:
                logging.info("[INFO] - Found match for zip and city")
                res = json.dumps(dict(error = False, is_valid = True, zip = zip_code, city = city_name))
            else: 
                logging.info(f"[INFO] - No match found for zip and city")
                res = json.dumps(dict(error = False, is_valid = False, has_options = False)) 
            return res

    class ValidateEMAIL(object):
        def __init__(self, config, manifest, values, region, locale, connector):
            # Import from main class
            self.config = config
            self.values = values
            self.region = region
            self.locale = locale
            self.manifest = manifest
            self.connector = connector
            self.cleaner = resolve.CleanText(locale, allowed_symbols=["_", "-", "@", "." ], 
                                             additional_symbols={"at":"@", "at.":"@"},
                                             extra_specials={"dot.com":".com"},
                                             extra_spelling_alphabet={})
            
        
        def remove_2dot(self, text):
            if '.' in text[-1]:
                text = text[:-1]
            regexlist = [
                        (r'dot(\.)', '.'),
                        (r'punkt(\.)', '.'), 
                        (r'(\.)(\.)', '.')
                        ]
            for regex in regexlist:
                text = re.sub(regex[0], regex[1], text)
               
            return text
        def run(self):
            r = luis.score(self.values["query"], self.connector.credentials, ATTRIBUTE_VALIDATOR_ENV, self.region)
            
            if 'email' in r['prediction']['entities']:
                email = "".join(self.remove_2dot(r['prediction']['entities']['email'][0]))
                return json.dumps(
                    {
                        "query": self.values["query"],
                        "e-mail recognized": True,
                        "e-mail": email,
                        "entities": r['prediction']['entities'],
                        "topScoringIntent": r['prediction']['topIntent']
                    }
                )
            elif 'email_spelled' in r['prediction']['entities']:
                email = self.cleaner.clean(r['prediction']['entities']['email_spelled'][0], convertsymbols=True, convertnumbers=True).replace(" ", "")
                email = "".join(self.remove_2dot(email))
                if "@" not in email:
                    return json.dumps(
                        {
                            "query": self.values["query"],
                            "e-mail recognized": False,
                            "e-mail": "",
                            "entities": r['prediction']['entities'],
                            "topScoringIntent": r['prediction']['topIntent']
                        }
                    )
                return json.dumps(
                    {
                        "query": self.values["query"],
                        "e-mail recognized": True,
                        "e-mail": email,
                        "entities": r['prediction']['entities'],
                        "topScoringIntent": r['prediction']['topIntent']
                    }
                )
            else:
                return json.dumps(
                    {
                        "query": self.values["query"],
                        "e-mail recognized": False,
                        "e-mail": "",
                        "entities": r['prediction']['entities'],
                        "topScoringIntent": r['prediction']['topIntent']
                    }
                )
# Global variables for request hanlding
CONFIG = "config"
INPUT = "input"
LOCALES = "locales"
LOCAL_DATA_PATH = "local_data_path"
MANIFEST = "manifest"
MODULE = "module"
MODULES = "modules"
REGION = "region"
VALUES = "values"
USE_DB = "use_db"

# API Names
AUTHENTICATOR = "Authenticator"
FORM_RECOGNIZER = "FormRecognizer"
LICENSE_PLATE_RECOGNIZER = "LicensePlateRecognizer"
TABLE_REQUESTOR = "TableRequestor"
VIN_RESOLVER = "VINResolver"

# API Names for Environment Variables
ATTRIBUTE_VALIDATOR_ENV = "ATTRIBUTE_VALIDATOR"
AUTHENTICATOR_ENV = "AUTHENTICATOR"
FORM_REGOGNIZER_ENV = "FORM_RECOGNIZER"
LICENSE_PLATE_RECOGNIZER_ENV = "LICENSE_PLATE_RECOGNIZER"
TABLE_REQUESTOR_ENV = "TABLE_REQUESTOR"
VIN_RESOLVER_ENV = "VIN_RESOLVER"

# Environment Variable Settings Lookup
SETTINGS_LOOKUP = {
    AUTHENTICATOR_ENV:              ["CONNECTION_STRING"],
    ATTRIBUTE_VALIDATOR_ENV:        ["CONNECTION_STRING"],
    FORM_REGOGNIZER_ENV:            ["NAME", "FR_TABLE_NAME", "CONNECTION_STRING", "RETURN_KEYS"],
    LICENSE_PLATE_RECOGNIZER_ENV:   ["LUIS_ID_{region_code}", "LUIS_KEY_{region_code}", "LUIS_PREDICTION_ENDPOINT_{region_code}", "LUIS_SLOT_{region_code}"],
    TABLE_REQUESTOR_ENV:            ["CONNECTION_STRING"],
    VIN_RESOLVER_ENV:               ["LUIS_ID_{region_code}", "LUIS_KEY_{region_code}", "LUIS_PREDICTION_ENDPOINT_{region_code}", "LUIS_SLOT_{region_code}"],
}

# Attribute Validator-specific assets
ATTRIBUTE_VALIDATOR = "AttributeValidator"
ATTRIBUTE_VALIDATOR_CITY_TABLE = "AttributeValidatorZIP"
ATTRIBUTE_VALIDATOR_ADDRESS_TABLE = "AttributeValidatorStreets"
ATTRIBUTE_LOOKUP_ZIP = "ZIP"
ATTRIBUTE_LOOKUP_STREET = "RowKey"
ADDRESS = "address"
CITY = "city"
HOUSE_NUMBER = "number"
IBAN = "iban"
STREET = "street"
STREET_IN_CITY = "street_in_city"
ZIP = "zip"
LEV_DISTANCE_INIT = 2

# Table Requestor data
CUSTOMER_DATA_TABLE = "CustomerData"
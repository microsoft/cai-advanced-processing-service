# Attribute Validators
CONFIG = "config"
MANIFEST = "manifest"
MODULES = "modules"
USE_DB = "use_db"
LOCAL_DATA_PATH = "local_data_path"

MODULE = "module"
INPUT = "input"
LOCALES = "locales"
REGION = "region"
VALUES = "values"

ATTRIBUTE_VALIDATOR = "AttributeValidator"
ATTRIBUTE_VALIDATOR_ENV = "ATTRIBUTE_VALIDATOR"
ATTRIBUTE_VALIDATOR_CITY_TABLE = "AttributeValidatorZIP"
ATTRIBUTE_VALIDATOR_ADDRESS_TABLE = "AttributeValidatorStreets"
ADDRESS = "address"
CITY = "city"
HOUSE_NUMBER = "number"
IBAN = "iban"
STREET = "street"
STREET_IN_CITY = "street_in_city"
ZIP = "zip"

LEV_DISTANCE_INIT = 2

ATTRIBUTE_LOOKUP_ZIP = "ZIP"
ATTRIBUTE_LOOKUP_STREET = "RowKey"

region = ""
SETTINGS_LOOKUP = {
    "VINResolver": [f"LUIS_ID_{region}", f"LUIS_KEY_{region}", f"LUIS_PREDICTION_ENDPOINT_{region}", f"LUIS_SLOT_{region}"],
    "LicensePlateRecognizer": [f"LUIS_ID_{region}"],
    "Authenticator": [f"CONNECTION_STRING"],
    "AttributeValidator": [f"CONNECTION_STRING"],
    "FormRecognizer": ["FR_NAME", "FR_TABLE_NAME", "FR_STORAGE_CONNECTION_STRING", "FR_RETURN_KEYS"]
}
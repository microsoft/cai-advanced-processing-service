import os
import sys
import logging
import configparser

def get_formrecognizer_connection_data():
    '''Retrieve connection data from environment variables or local config'''
    # Model ID from when you trained your model.
    endpoint = f"https://{os.environ.get('FORM_RECOGNIZER_NAME')}.cognitiveservices.azure.com"
    key = os.environ.get("FORM_RECOGNIZER_KEY")
    connection_data = {}
    connection_data['table_name'] = os.environ.get("FR_TABLE_NAME")
    connection_data['connection_string'] = os.environ.get("FR_STORAGE_CONNECTION_STRING")
    return_keys = os.environ.get("FR_RETURN_KEYS")

    # If environment variables do not exist, we enter local debugging using a config.ini
    if not endpoint or not key:
        # Local debugging
        logging.warning("No environment variable found, entered local debugging")
        sys.path.append('./')
        config = configparser.ConfigParser()
        config.read('config.ini')
        endpoint = f"https://{config['formrec']['name']}.cognitiveservices.azure.com"
        key = config['formrec']['key']
        return_keys = config['formrec']['FR_RETURN_KEYS']
        # Prepare connection data as dict
        connection_data = {}
        connection_data['table_name'] = config['formrec']['FR_TABLE_NAME']
        connection_data['connection_string'] = config['formrec']['FR_STORAGE_CONNECTION_STRING'].replace('"', '')
    return connection_data, return_keys, endpoint, key
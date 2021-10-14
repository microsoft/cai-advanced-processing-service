import configparser
import os
import logging
def get_connection_data():
    connection_data = dict()
    try:
        connection_data['container'] = os.environ.get('AZURE_BLOB_CONTAINER')
        connection_data['connection_string'] = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        connection_data['table_name'] = os.environ.get('AZURE_TABLE_NAME')
        connection_data['user'] = os.environ.get('APP_USER')
        connection_data['password'] = os.environ.get('APP_PASSWORD')
        connection_data['app_id'] = os.environ.get('LUIS_APP_ID')
        connection_data['key'] = os.environ.get('LUIS_KEY')
        connection_data['endpoint'] = os.environ.get('LUIS_ENDPOINT')
        connection_data['slot'] = os.environ.get('LUIS_SLOT')
        logging.info('Reading info and keys from app settings')
    except Exception as e:
        config = configparser.ConfigParser()
        config.read('../config.ini')
        connection_data['container'] = config['AZURE']['BLOB_CONTAINER']
        connection_data['connection_string'] = config['AZURE']['STORAGE_CONNECTION_STRING']
        connection_data['table_name'] = config['AZURE']['TABLE_NAME']
        connection_data['user'] = config['CRED']['USER_NAME']
        connection_data['password'] = config['CRED']['PASSWORD']
        connection_data['app_id'] = config['LUIS']['APP_ID']
        connection_data['key'] = config['LUIS']['KEY']
        connection_data['endpoint'] = config['LUIS']['ENDPOINT']
        connection_data['slot'] = config['LUIS']['SLOT']
        logging.warning('Reading info and keys from local config')
    return connection_data
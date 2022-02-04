''' TABLE REQUEST MODULE '''
import os
import sys
import logging
import configparser
from azure.cosmosdb.table import TableService
from azure.common import AzureMissingResourceHttpError

class CredentialRetriever;
    def __init__():
        pass

    def get_table_creds(application_name):
        '''Retrieve connection data from environment variables or local config'''
        try:
            # Load environment variables first
            auth_attributes = {item: os.environ.get(item) for item in [f"{application_name}_CONNECTION_STRING"]}
            # If environment variables could not be loaded, we gather them from a local config
            if None in auth_attributes.values():
                # Local debugging
                logging.info("[INFO] - No environment variable found, entered local debugging")
                sys.path.append('./')
                config = configparser.ConfigParser()
                config.read('config.ini')
                auth_attributes = {item: config[application_name][item].replace('"', '') for item in [f"{application_name}_CONNECTION_STRING"]}
                logging.info('[INFO] - Loaded connection attributes from locale config file.')
        except KeyError:
            auth_attributes = None
            logging.error('[ERROR] - Could not retrieve connection attributes, please verify they are correctly set.')
        return auth_attributes

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


class DataConnector:
    def __init__():
        pass



    def get_data_from_table(connection_data, table_name, application_name, table_filters=None):
        ''' Send request to authentication data table '''
        # Build connection data
        table_service = TableService(connection_string = connection_data[f"{application_name}_CONNECTION_STRING"])
        # Assemble filters to a valid request, if not None
        if table_filters is not None:
            _filter = " and ".join([f"{key} eq '{table_filters[key]}'" for key, _ in table_filters.items()])
        else:
            _filter = None
        # Send request to table storage
        try:
            customer_data = table_service.query_entities(table_name=table_name, filter=_filter, timeout=5)
        except AzureMissingResourceHttpError:
            logging.error()
            customer_data = None
        # TODO: Improve error handling
        return customer_data.items

    def push_data_to_table(connection_data, application_name, data):
        ''' Insert new data into table storage '''
        # Build connection data
        table_service = TableService(connection_string = connection_data[f"{application_name}_CONNECTION_STRING"])
        # Send insert request
        table_service.insert_or_replace_entity(connection_data[f"{application_name}_TABLE_NAME"], data)


def main():
    customer_data = get_data_from_table(connection_data, application_name, table_filters)
    return customer_data

if __name__ == "__main__":
    # Example inputs
    application_name = "ATTRIBUTE_VALIDATOR"
    connection_data = {f"{application_name}_TABLE_NAME": 'ZIP', f"{application_name}_CONNECTION_STRING": ""}
    table_filters = {'PartitionKey': 'DE'}
    # table_filters = None # If no filters should be applied

    # Run request
    customer_data = main()
    for customer in customer_data:
        logging.warning(customer)
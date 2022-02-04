''' TABLE REQUEST MODULE '''
import os
import sys
import logging
import configparser
from azure.cosmosdb.table import TableService
from azure.common import AzureMissingResourceHttpError

from assets.constants import SETTINGS_LOOKUP

# config.ini
# [MODULE_NAME]
# KEY=
# MODULE_NAME_KEY

class CredentialRetriever:
    def __init__(self, module, variables):
        self.module = module
        self.variables = variables
        self.credentials = SETTINGS_LOOKUP[module]

    def load_credentials(self):
        try:
            # Load environment variables first
            self.authentication_attributes = self._get_from_appsettings() 
            # If environment variables could not be loaded, we gather them from a local config
            if None in self.authentication_attributes.values():
                self.authentication_attributes = self._get_from_configfile()
        except KeyError:
            self.authentication_attributes = None
            logging.error('[ERROR] - Could not retrieve connection attributes, please verify they are correctly set.')
        return self.authentication_attributes

    def _get_from_configfile(self):
        '''Retrieve connection data from local config file'''
        self.authentication_attributes = {item: os.environ.get(item) for item in self.variables}
        logging.info("[INFO] - No environment variable found, entered local debugging")
        sys.path.append('./')
        config = configparser.ConfigParser()
        config.read('config.ini')
        return {item: config[self.module][item].replace('"', '') for item in self.variables}
    
    def _get_from_appsettings(self):
        '''Retrieve connection data from app settings'''
        return {item: os.environ.get(item) for item in self.variables}

class DataConnector:
    def __init__(self, use_db=True, local_file_path=None):
        self.use_db = use_db
        self.local_file_path = local_file_path
        if self.use_db:
            self.connector = self.LocalDataConnector
        else:
            self.connector = self.AzureDataConnector

    class LocalDataConnector:
        def __init__(self):
            pass

        def get_data(self):
            pass

        def push_data(self):
            pass

    class AzureDataConnector:
        def __init__(self):
            pass

        def get_data(self, connection_data, table_name, application_name, table_filters=None):
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

        def push_data(self, connection_data, application_name, data):
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
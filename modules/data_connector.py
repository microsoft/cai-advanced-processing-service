''' TABLE REQUEST MODULE '''
import logging
from azure.cosmosdb.table import TableService
from azure.common import AzureMissingResourceHttpError

from assets.constants import (
    USE_DB
)

class DataConnector:
    def __init__(self, app, config, credentials):
        self.app = app
        self.config = config
        self.credenitals = credentials
        # Depending on whether we use db or not, we decide which data connector will be activated
        if self.config.get(USE_DB):
            logging.info('[INFO] - Setting up Azure data connector.')
            self.connector = self.AzureDataConnector(self.app, self.credenitals)
        else:
            logging.info('[INFO] - Setting local data connector.')
            self.connector = self.LocalDataConnector(self.app, self.config)

    class LocalDataConnector:
        def __init__(self, app, config):
            # self.app = app for folder to find stuff in 
            self.app = app
            self.local_file_path = config.get('local_file_path')

        def get_data(self):
            pass

        def push_data(self):
            pass

    class AzureDataConnector:
        def __init__(self, app, credentials):
            self.app = app
            self.credentials = credentials

        def get_data(self, table_name, table_filters=None):
            ''' Send request to authentication data table '''
            # Build connection data
            table_service = TableService(connection_string = self.credentials[f"{self.app}_CONNECTION_STRING"])
            # Assemble filters to a valid request, if not None
            if table_filters is not None:
                _filter = " and ".join([f"{key} eq '{table_filters[key]}'" for key, _ in table_filters.items()])
            else:
                _filter = None
            # Send request to table storage
            try:
                customer_data = table_service.query_entities(table_name = table_name, filter = _filter, timeout = 5)
            except AzureMissingResourceHttpError:
                logging.error()
                customer_data = None
            # TODO: Improve error handling
            return customer_data.items

        def push_data(self, connection_data, data):
            ''' Insert new data into table storage '''
            # Build connection data
            table_service = TableService(connection_string = self.credentials[f"{self.app}_CONNECTION_STRING"])
            # Send insert request
            table_service.insert_or_replace_entity(connection_data[f"{self.app}_TABLE_NAME"], data)

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
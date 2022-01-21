''' TABLE REQUEST MODULE '''
import os
import sys
import logging
import configparser
from azure.cosmosdb.table import TableService

# Example inputs
connection_data = {'table_name': 'CustomerData', 'connection_string': ""}
table_filters = {'PartitionKey': 'CustomerData'}
# table_filters = None # If no filters should be applied

def get_table_creds(connection_attributes):
    '''Retrieve connection data from environment variables or local config'''
    try:
        auth_attributes = {item: config['userdata'][item] for item in connection_attributes}
        logging.info('[INFO] - Loaded connection attributes from locale config file.')
        # Load environment variables first
        auth_attributes = {item: os.environ.get(item) for item in connection_attributes}
        # If environment variables could not be loaded, we gather them from a local config
        if None in auth_attributes.values():
            # Local debugging
            logging.warning("No environment variable found, entered local debugging")
            sys.path.append('./')
            config = configparser.ConfigParser()
            config.read('config.ini')        
    except KeyError:
        auth_attributes = None
        logging.warning('[WARNING] - Loaded connection attributes from locale config file.')
    return auth_attributes

def get_data_from_table(connection_data, table_filters=None):
    ''' Send request to authentication data table '''
    # Build connection data
    table_service = TableService(connection_string = connection_data['connection_string'])
    # Assemble filters to a valid request, if not None
    if table_filters is not None:
        _filter = " and ".join([f"{key} eq '{table_filters[key]}'" for key, _ in table_filters.items()])
    else:
        _filter = None
    # Send request to table storage
    customer_data = table_service.query_entities(connection_data['table_name'], filter=_filter)
    return customer_data.items

def push_data_to_table(connection_data, data):
    ''' Insert new data into table storage '''
    # Build connection data
    table_service = TableService(connection_string = connection_data['connection_string'])
    # Send insert request
    table_service.insert_or_replace_entity(connection_data['table_name'], data)

def main():
    customer_data = get_data_from_table(connection_data, table_filters)
    return customer_data

if __name__ == "__main__":
    customer_data = main()
    for customer in customer_data:
        logging.info(customer)
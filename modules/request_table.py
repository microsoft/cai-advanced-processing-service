''' TABLE REQUEST MODULE '''
import os
import logging
from azure.cosmosdb.table import TableService, Entity

# Example inputs
connection_data = {'table_name': 'CustomerData', 'connection_string': "DefaultEndpointsProtocol=https;AccountName=jagotestingfunctions;AccountKey=/ED2eAurl0DIZIedulyj9JYCTbvpQqSm5KSfmi8g/NVDEGNLO36YG7jRKZK4Juxwcst2GpNzQ4UmPZg+fsiPxw==;EndpointSuffix=core.windows.net"}#, 'connection_string': "DefaultEndpointsProtocol=https;AccountName=nonstopstore;AccountKey=3EDZulLhsAARroSnPKLl9FO+YeJPQLbrX8A2P9RIR1otCZa7iropkwYSQYKpr7CLNZ1kxl2B4OYTrDBCNc6k5g==;EndpointSuffix=core.windows.net"}
table_filters = {'PartitionKey': 'CustomerData'}
# table_filters = None # If no filters should be applied

def get_data_from_table(connection_data, table_filters=None):
    ''' Send request to authentication data table '''
    # Build connection data
    table_service = TableService(connection_string=connection_data['connection_string'])
    # Assemble filters to a valid request, if not None
    if table_filters is not None:
        _filter = " and ".join([f"{key} eq '{table_filters[key]}'" for key, value in table_filters.items()])
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
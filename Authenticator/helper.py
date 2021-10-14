import os
import logging
import configparser
import sys

def get_connection_data(connection_attributes):
    '''Retrieve connection data from environment variables or local config'''
    # Load environment variables first
    auth_attributes = {item:os.environ.get(item) for item in connection_attributes}
    # If environment variables could not be loaded, we gather them from a local config
    if None in auth_attributes.values():
        # Local debugging
        logging.warning("No environment variable found, entered local debugging")
        sys.path.append('./')
        config = configparser.ConfigParser()
        config.read('config.ini')
        auth_attributes = {item:config['userdata'][item] for item in connection_attributes}
    return auth_attributes


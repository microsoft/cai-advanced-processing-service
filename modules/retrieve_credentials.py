
import os
import sys
import logging
import configparser

# Import custom modules
from assets.constants import SETTINGS_LOOKUP

class CredentialRetriever:
    def __init__(self, app):
        self.app = app
        self.required_credentials = SETTINGS_LOOKUP[self.app]

    def load_credentials(self, normalize=False):
        '''Load credentials from environment variables or configs
        Args:
            normalize tuple of strings
        Returns:
            authentication_attributes dict'''
        try:
            # Load environment variables first
            self.authentication_attributes = self._get_from_appsettings() 
            # If environment variables could not be loaded, we gather them from a local config
            if None in self.authentication_attributes.values():
                self.authentication_attributes = self._get_from_configfile()
        except KeyError:
            self.authentication_attributes = None
            logging.error('[ERROR] - Could not retrieve connection attributes, please verify they are correctly set.')
        finally:
            if normalize:
                self.authentication_attributes = [attribute.replace(normalize[0], normalize=[1]) for attribute in self.authentication_attributes]
        return self.authentication_attributes

    def _get_from_configfile(self):
        '''Retrieve connection data from local config file'''
        logging.info("[INFO] - No environment variable found, entered local debugging")
        sys.path.append('./')
        config = configparser.ConfigParser()
        config.read('config.ini')
        logging.warning({f'{self.app}_{item}': config[self.app][item].replace('"', '') for item in self.required_credentials})
        return {f'{self.app}_{item}': config[self.app][item].replace('"', '') for item in self.required_credentials}
    
    def _get_from_appsettings(self):
        '''Retrieve connection data from app settings'''
        return {item: os.environ.get(item) for item in self.required_credentials}
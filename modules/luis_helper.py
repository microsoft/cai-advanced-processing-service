'''LUIS HELPER'''
import requests
import logging
import json
import os

# Define logger
logger = logging.getLogger(__name__)

# LUIS Scoring
def score_luis(text, credentials):
    """Score LUIS endpoint (REST API v3) and return parsed JSON"""

    # Set header/params for rest call
    params = {
        'q': text,
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }
    headers = {
        'Ocp-Apim-Subscription-Key': credentials['luis_key'],
    }

    # Set URL parameters to use in this REST call.
    params ={
        'query': text,
        'timezoneOffset': '0',
        'verbose': 'true',
        'show-all-intents': 'true',
        'spellCheck': 'false',
        'staging': 'false',
        'subscription-key': credentials['luis_key']
    }

    # Set connection URL
    url = f'https://{credentials["luis_prediction_endpoint"]}.cognitiveservices.azure.com/luis/prediction/v3.0/apps/{credentials["luis_id"]}/slots/{credentials["luis_slot"]}/predict'

    # Make the REST call.
    try:
        response = requests.get(url, headers = headers, params = params)
        response = json.loads(r.text)
        logger.info('[INFO] - successfully processed LUIS request')
    except Exception as e:
        logger.error(f"[ERROR] LUIS encountered an issue -> {e}.")
    return response
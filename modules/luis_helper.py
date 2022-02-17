'''LUIS HELPER'''
import requests
import logging
import json

# Define logger
logger = logging.getLogger(__name__)

# LUIS Scoring
def score(text, credentials, app, lang):
    """Score LUIS endpoint (REST API v3) and return parsed JSON"""
    # Set environment variables
    lang = lang.upper()
    luis_key = credentials[f'{app}_LUIS_KEY_{lang}']
    luis_endpoint = credentials[f'{app}_LUIS_PREDICTION_ENDPOINT_{lang}']
    luis_id = credentials[f'{app}_LUIS_ID_{lang}']
    luis_slot = credentials[f'{app}_LUIS_SLOT_{lang}']

    # Set params for REST call.
    params = {
        'q': text,
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }
    # Set header for REST call.
    headers = {}

    # Set URL parameters to use in this REST call.
    params = {
        'query': text,
        'timezoneOffset': '0',
        'verbose': 'true',
        'show-all-intents': 'true',
        'spellCheck': 'false',
        'staging': 'false',
        'subscription-key': luis_key
    }

    # Set connection URL
    url = f'https://{luis_endpoint}/luis/prediction/v3.0/apps/{luis_id}/slots/{luis_slot}/predict'

    # Make the REST call
    try:
        response = requests.get(url, headers = headers, params = params)
        response = json.loads(response.text)
        logger.info('[INFO] - successfully processed LUIS request')
    except Exception as e:
        logger.error(f"[ERROR] LUIS encountered an issue -> {e}.")
    return response
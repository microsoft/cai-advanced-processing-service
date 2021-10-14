import json
import logging
import time
import sys
import requests

def test_spelling_resolver(r):
  # Unit URL
  url = "http://localhost:7071/api/SpellingResolver"

  payload = json.dumps({
    "text": r
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)

  res = json.loads(response.text)['first_letters_nospace']
  logging.warning(res)
  return res
import json
import logging
import time
import sys
import requests

def test_VINResolver(r, region="de", locale="de"):
  # Unit URL
  url = "http://localhost:7071/api/VINResolver"

  payload = json.dumps({
    "query": r,
    "expectedwmi": ["WDI"],
    "locale": locale
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  res = json.loads(response.text)
  
  return res, response.status_code
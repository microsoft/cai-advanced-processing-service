import json
import logging
import time
import sys
import requests

def test_licenseplaterecognizer(r, region="de", locale="de"):
  # Unit URL
  url = "http://localhost:7071/api/LicensePlateRecognizer"

  payload = json.dumps({
    "query": r,
    "region": region,
    "locale": locale
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  res = json.loads(response.text)
  
  return res['cplEntities'][0]['entity']
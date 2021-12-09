import logging

import azure.functions as func
from modules.libvin import Vin
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    vin = req.params.get('vin')
    if not vin:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            vin = req_body.get('vin')

    if vin:
        v = Vin(vin)
        
        
        vin_json = {
            "region": v.region,
            "country": v.country,
            "year": v.year,
            "male": v.make,
            "manufacturer": v.manufacturer,
            "is_pre_2010": v.is_pre_2010,
            "wmi": v.wmi,
            "vds": v.vds,
            "vis": v.vis,
            "vsn": v.vsn,
            "less_than_500_built_per_year": v.less_than_500_built_per_year
        } 
        
        return func.HttpResponse(
            json.dumps(vin_json),
            mimetype="application/json",
        )
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a Vehicle Identification Numbers in the query string or in the request body for a personalized response.",
             status_code=200
        )

'''VIN RESOLVER'''
import json
import logging
import azure.functions as func

# Define global logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
for handler in logger.handlers:
    if isinstance(handler, logging.Streamhandler):
        handler.setFormatter(formatter)

# Import custom modules
from modules.libvin import Vin
from modules import luis_helper as luis
from modules import resolve_spelling as resolve
from modules.retrieve_credentials import CredentialRetriever
from assets.constants import CONFIG, MANIFEST, VIN_RESOLVER_ENV

def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('[INFO] VINResolver Post Processing started.')

    # Get query and request parameters
    try:
        req_body    = req.get_json()
        query       = req_body.get('query')
        expectedwmi = [i.upper() for i in req_body.get('expectedwmi')]
        lang        = req_body.get('locale')
    except Exception as e:
        logger.info(f'[INFO] Trying to receive request via params -> {e}')
        query       = req.params.get('query')
        expectedwmi = req.params.get('expectedwmi')
        lang        = req.params.get('locale')
    finally:    
        # Fill eventually missing params with default ones
        if not lang:
            lang = 'de'
        if not expectedwmi:
            expectedwmi = 'WDC'
        
        # Snip off everything after first three characters 
        expectedwmi = expectedwmi[:3]
         # Snip off everything after first two characters (e.g. en-us -> en)
        lang = lang[:2]
        logger.info(f'[INFO] - Set params -> expectedwmi: {expectedwmi}, language: {lang}.')

    msg = []
    # Retrieve credentials
    credentials = CredentialRetriever(VIN_RESOLVER_ENV, normalize=('{region_code}', lang)).load_credentials()
    
    # define cleaner
    cleaner = resolve.CleanText(lang, allowed_symbols=['-', '*'], additional_symbols={})

    if credentials is None:
        return func.HttpResponse(
             "[ERROR] Locale not supported",
             status_code = 400
        )

    # If query is not empty, go ahead
    elif query:
        # Get LUIS entity results
        r = luis.score(query, credentials, VIN_RESOLVER_ENV, lang)
        # if 'vin' in r['prediction']['entities']:
        try:
            ## Load entity
            entity = r['prediction']['entities']['vin'][0].lower()
            topScoringIntent = r['prediction']['topIntent']
        except KeyError:
            entity = query.lower()
            topScoringIntent = r['prediction']['topIntent']
            msg.append('[WARNING] - No entity could be extracted')
        except Exception as e:
            logger.error(f'[ERROR] - {e}')
            msg.append(f'[ERROR] - {e}')
            entity = query.lower()
            
        entity = cleaner.clean(entity, convertsymbols=False, convertnumbers=True).replace(" ", "")

        # Get VIN entity results
        v = Vin(entity)
        
        # if VIN is valid, go ahead
        if v.wmi and v.vds and v.vis and v.vsn is not None:
            ## Pack json response
            res = json.dumps(
                {
                    "query": query,
                    "vinQuery": entity,
                    "validvin": v.is_valid,
                    "expectedwmi": v.wmi.upper() in expectedwmi,
                    "vindetails": {
                        "region": v.region,
                        "country": v.country,
                        "validvin": v.is_valid,
                        "year": v.year,
                        "make": v.make,
                        "manufacturer": v.manufacturer,
                        "is_pre_2010": v.is_pre_2010,
                        "wmi": v.wmi,
                        "vds": v.vds,
                        "vis": v.vis,
                        "vsn": v.vsn,
                        "less_than_500_built_per_year": v.less_than_500_built_per_year
                    },
                    "entities": r['prediction']['entities'],
                    "topScoringIntent": topScoringIntent
                })
                    
        else:
            ## Pack json response
            res = json.dumps(
                {
                "query": query,
                "validvin": False,
                "vindetails": {},
                "entities": r.get('prediction', None).get('entities', None),
                "message": msg
                }
                )

        return func.HttpResponse(
            res, mimetype='application/json'
        )   

    else:
        return func.HttpResponse(
            "[ERROR] Received a blank request. Please pass a value using the defined format. Example: {'query':'das ist 2A4GM684X6R632476', 'expectedwmi': ['WDC'],'locale': 'de'}",
            status_code = 400
            )

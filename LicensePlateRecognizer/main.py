''' LICENSE PLATE RECOGNIZER API '''
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

# Import custom modules and helpers
from modules import license_plate_recognizer as lpr
from modules import request_luis

def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('[INFO] LicensePlate Post Processing started.')

    # Get query and request parameters
    try:
        req_body = req.get_json()
        query = req_body.get('query')
        region = req_body.get('region')
        lang = req_body.get('locale')
    except Exception as e:
        logger.info(f'[INFO] Trying to receive request via params -> {e}')
        query = req.params.get('query')
        region = req.params.get('region')
        lang = req.params.get('locale')
    finally:    
        # Fill eventually missing params with default ones
        if not lang and not region:
            lang = 'de'
            region = lang
        elif not lang and region: 
            lang = region
        elif lang and not region:
            region = lang
        # Snip off everything after first two characters (e.g. en-us -> en)
        region = region[:2]
        lang = lang[:2]
        logger.info(f'[INFO] Set params -> region: {region}, language: {lang}.')
    
    # Create instance of class with locale
    matcher = lpr.LicensePlateRecognizer(region, lang).matcher
    # Load luis credentials 
    luis_creds = request_luis.get_luis_creds(region)

    # If query is not empty, go ahead
    if query and matcher is not None:
        # Get LUIS entity results
        r = request_luis.score_luis(query, luis_creds)
        try:
            r_ent = r['prediction']['entities']['$instance']['platenumber'][0]
        except KeyError:
            logger.error('[WARNING] - No entity could be extracted')
            r_ent = None
        except Exception as e:
            logger.error(f'[ERROR] - {e}')
            r_ent = None

        # Process LP 
        if r_ent is not None:
            if r_ent.get('type') == 'licenseplate' or r_ent.get('type') == 'platenumber':
                ## Load entity
                start = r_ent["startIndex"]
                end = r_ent["startIndex"] + r_ent["length"]
                entity = query[start:end + 1].lower()

                ## License Plate Recognizer
                entity, ambig   =   matcher.clean(entity)
                raw, lp, split, valid    =   matcher.get_lp(query, entity)

                ## Format response
                cpl_entities, cpl_query = matcher.format_output(query, lp, split, valid, start, end, ambig)
                
                ## Pack json response
                res = json.dumps(dict(
                        id              =   1,
                        query           =   query,
                        cplQuery        =   cpl_query,
                        cplEntities     =   cpl_entities,
                        entities        =   [r_ent],
                        topScoringIntent=   r.get('prediction').get('topIntent')
                        )
                    )
        else:
            ## Pack json response
            res = json.dumps(dict(
                    id              =   1,
                    query           =   query,
                    cplQuery        =   query,
                    cplEntities     =   [],
                    entities        =   r.get('prediction').get('entities'),
                    topScoringIntent=   r.get('prediction').get('topIntent')
                    )
                )
        return func.HttpResponse(
            res, mimetype='application/json'
        )
    elif matcher is None or luis_creds is None:
        return func.HttpResponse(
             "[ERROR] Locale not supported",
             status_code = 400
        )
    else:
        return func.HttpResponse(
             "[ERROR] Received a blank request. Please pass a value using the defined format. Example: \{'query':'AB C 1234'\}",
             status_code = 400
        )

        
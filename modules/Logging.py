import logging
import socket
import os

def host_log_adapter(logger):
    hostname = {"hostname": socket.gethostname()}
    return logging.LoggerAdapter(logger, hostname)

detailed_logging = os.environ.get('DETAILED_LOGGING_IS_ON')

# if default logging policy is not set, always default to not log
if detailed_logging is None:
    logs = False
else:
    logs = detailed_logging == "true"
log_query = str(logs)


# adds a configured stream handler to the root logger
syslog = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(levelname)s] %(message)s')
syslog.setFormatter(formatter)

logger = logging.getLogger()
logger.handlers = []       
logger.addHandler(syslog)

if (logs == True or log_query.lower() == "true") and log_query.lower() != "false":
    syslog.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.info("Detailed logging enabled")
else:
    syslog.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.info("Detailed logging disabled")

logger = host_log_adapter(logging.getLogger())




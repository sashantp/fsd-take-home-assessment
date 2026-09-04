import os
import json
import logging
import re

from utils import Utils
from couch_db_client import CouchDBClient
from datetime import datetime
from json import JSONDecodeError


# Configure logging settings
logging.basicConfig(
    filename='data_ingestion_service.log',
    filemode='a', # 'a' to append, 'w' to overwrite each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO # Capture INFO, WARNING, ERROR, and CRITICAL logs
)

logger = logging.getLogger(__name__)


def write_to_database(filepath:str, couch_db_client, details):

	try:
		with open(filepath, 'r', encoding='utf-8') as file:
			events = json.loads(file.read())

			for event in events:

				if not couch_db_client.exists(event[details['row_id']]):
					event['_id'] = event[details['row_id']]
					event['type'] = details['type']
					event['reconciled_event'] = False
					couch_db_client.create(event)
					logging.info(f"Events {event['_id']} of type {event['type']} written to database.")
				else:
					event['type'] = details['type']
					event['reconciled_event'] = False
					couch_db_client.update(event[details['row_id']], event)
					logging.info(f"Events {event['_id']} of type {event['type']} exists already.")

	except FileNotFoundError:
		logging.error("Error: The file was not found.")
	except JSONDecodeError as e:
		logging.error(f"Error: Invalid JSON formatting (Line {e.lineno}, Column {e.colno}).")



if __name__ == '__main__':

	cwd = os.getcwd()

	file_parser_callback_map = {'crm_events.json': Utils.parse_and_normalise_crm_event}

	files = {
				'crm_events.json': {'id': 'crm_events', 'type':'crm_event', 'row_id':'crm_id'},
				'calendar_events.json': {'id': 'calendar_events', 'type':'calendar_event', 'row_id':'event_id'}
			}

	couch = CouchDBClient(
	    url=os.getenv(
	        "COUCHDB_URL",
	        "http://localhost:5984/"
	    ),
	    username=os.getenv(
	        "COUCHDB_USERNAME",
	        "admin"
	    ),
	    password=os.getenv(
	        "COUCHDB_PASSWORD",
	        "password"
	    ),
	    database=os.getenv(
	        "COUCHDB_DATABASE",
	        "assessment"
	    )
	)

	couch.connect()

	for filename, details in files.items():

		write_to_database(f"{cwd}/data/{filename}", couch, details)
import os
import json
import logging
import re

from utils import Utils
from couch_db_client import CouchDBClient
from datetime import datetime
from json import JSONDecodeError
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path


# Configure logging settings
logging.basicConfig(
    filename='app.log',
    filemode='a', # 'a' to append, 'w' to overwrite each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO # Capture INFO, WARNING, ERROR, and CRITICAL logs
)




def load_data_from_file(filepath:str, vector_store: Chroma, parsing_callback_func):

	try:
		documents = []

		with open(filepath, 'r', encoding='utf-8') as file:
			events = json.loads(file.read())
			for record in events:

				try:
					text = ""
					logging.info(f"Inserting record in vector store")
					text, metadata = parsing_callback_func(record)

					if len(text) > 0:
						document = Document(page_content=text, metadata=metadata)
						documents.append(document)

				except Exception as exp:

					logging.error(f"Error for record {record}")
					logging.error(exp)

		text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
		all_splits = text_splitter.split_documents(documents)
		logging.info(f"Split documentation into {len(all_splits)} chunks.")

		vector_store.add_documents(documents=all_splits)
		logging.info(f"Indexed {len(all_splits)} chunks.")

	except FileNotFoundError:
		logging.error("Error: The file was not found.")
	except JSONDecodeError as e:
		logging.error(f"Error: Invalid JSON formatting (Line {e.lineno}, Column {e.colno}).")


def write_to_database(filepath:str, couch_db_client, details):

	try:
		with open(filepath, 'r', encoding='utf-8') as file:
			events = json.loads(file.read())

			for event in events:

				event['_id'] = event[details['row_id']]
				event['type'] = details['type']
				event['reconciled_event'] = False

				couch_db_client.create(event)

				logging.info(f"Events {event['_id']} of type {event['type']} written to database")

	except FileNotFoundError:
		logging.error("Error: The file was not found.")
	except JSONDecodeError as e:
		logging.error(f"Error: Invalid JSON formatting (Line {e.lineno}, Column {e.colno}).")



if __name__ == '__main__':

	cwd = os.getcwd()

	embeddings = OllamaEmbeddings(model="nomic-embed-text")

	# knowledgebase vector store
	vector_store = Chroma(
	    collection_name="meetings",
	    embedding_function=embeddings,
	    persist_directory=f"{cwd}/chroma_langchain_db",  # Where to save data locally, remove if not necessary
	)


	data_dir = Path("data").resolve()

	file_parser_callback_map = {'crm_events.json': Utils.parse_and_normalise_crm_event}

	# for filename , parsing_callback_func in file_parser_callback_map.items():

	# 	load_data_from_file(f"{cwd}/data/{filename}", vector_store, parsing_callback_func)

	files = {
				'crm_events.json': {'id': 'crm_events', 'type':'crm_event', 'row_id':'crm_id'},
				'calendar_events.json': {'id': 'calendar_events', 'type':'calendar_event', 'row_id':'event_id'}
			}

	couch = CouchDBClient(
	    url="http://localhost:5984/",
	    username="admin",
	    password="password",
	    database="assessment"
	)

	couch.connect()

	for filename, details in files.items():

		write_to_database(f"{cwd}/data/{filename}", couch, details)
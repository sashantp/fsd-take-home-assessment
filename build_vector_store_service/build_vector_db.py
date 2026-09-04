import os
import json
import logging

from couch_db_client import CouchDBClient
from json import JSONDecodeError
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils import Utils


# Configure logging settings
logging.basicConfig(
    filename='vector_app.log',
    filemode='a', # 'a' to append, 'w' to overwrite each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO # Capture INFO, WARNING, ERROR, and CRITICAL logs
)

logger = logging.getLogger(__name__)


def load_data_to_vector(couch:CouchDBClient, event_type:str, vector_store: Chroma, parsing_callback_func):

	try:
		documents = []

		events = couch.find_by_attribute(attribute='type', value=event_type)

		logging.info(events)

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
				logger.exception(f"Error for record id : {record['crm_id']}")


		text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
		all_splits = text_splitter.split_documents(documents)
		logging.info(f"Split documentation into {len(all_splits)} chunks.")

		vector_store.add_documents(documents=all_splits)
		logging.info(f"Indexed {len(all_splits)} chunks.")

	except FileNotFoundError:
		logging.error("Error: The file was not found.")
	except JSONDecodeError as e:
		logging.error(f"Error: Invalid JSON formatting (Line {e.lineno}, Column {e.colno}).")


if __name__ == "__main__":

	cwd = os.getcwd()

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
	
	ollama_url = os.getenv("OLLAMA_BASE_URL","http://localhost:11434")

	embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

	vector_store = Chroma(
			collection_name="meetings",
			embedding_function=embeddings,
		    persist_directory=f"{cwd}/chroma_langchain_db"
		)

	llm = ChatOllama(
			model='qwen2.5:1.5b',
			base_url=ollama_url,
			temperature=0.5
		)

	file_parser_callback_map = {'crm_event': Utils.parse_and_normalise_crm_event}

	for event_type , parsing_callback_func in file_parser_callback_map.items():
		load_data_to_vector(couch, event_type, vector_store, parsing_callback_func)
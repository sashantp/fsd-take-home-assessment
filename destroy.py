import couchdb
import os
import json
import logging
import shutil

from couch_db_client import CouchDBClient
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


# Configure logging settings
logging.basicConfig(
    filename='logs/destroy_app.log',
    filemode='a', # 'a' to append, 'w' to overwrite each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO # Capture INFO, WARNING, ERROR, and CRITICAL logs
)

logger = logging.getLogger(__name__)


def delete_couch_database():
	# Connect to the CouchDB server
	server = couchdb.Server('http://localhost:5984/')
	server.resource.credentials = ('admin','password')

	# Drop/Delete the database
	db_name = 'assessment'
	if db_name in server:
		del server[db_name]
		logging.info(f"Database '{db_name}' dropped successfully.")
	else:
		logging.info(f"Database '{db_name}' does not exist.")


def destroy_vector_database():

	cwd = os.getcwd()

	ollama_url = os.getenv("OLLAMA_BASE_URL","http://localhost:11434")

	embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

	collection_name = 'meetings'

	persist_directory=f"{cwd}/chroma_langchain_db"

	vector_store = Chroma(
			collection_name="meetings",
			embedding_function=embeddings,
		    persist_directory=f"{cwd}/chroma_langchain_db"
		)

	vector_store.delete_collection()

	logging.info(f"Vector store '{collection_name}' deleted successfully.")

	if os.path.exists(persist_directory):
		shutil.rmtree(persist_directory)
		logging.info(f"Vector store dir '{persist_directory}' contents deleted successfully.")
	else:
		logging.info(f"Vector store dir '{persist_directory}' does not exists.")


if __name__ == "__main__":

	delete_couch_database()
	# destroy_vector_database()
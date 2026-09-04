import os
import json
import logging
import numpy as np

from couch_db_client import CouchDBClient
from json import JSONDecodeError
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from json import JSONDecodeError
from pydantic import BaseModel
from utils import Utils


# Configure logging settings
logging.basicConfig(
    filename='reconcile_app.log',
    filemode='a', # 'a' to append, 'w' to overwrite each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO # Capture INFO, WARNING, ERROR, and CRITICAL logs
)

logger = logging.getLogger(__name__)


class MatchResult(BaseModel):
    matched: bool
    similarity_score: float
    reason: str


def compare_texts(embeddings_model:OllamaEmbeddings, text1: str, text2: str, threshold: float):
    
    try:
        embedding1 = embeddings_model.embed_query(text1)
        embedding2 = embeddings_model.embed_query(text2)
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        logging.info(f"Compare text on cosine similarity {cosine_similarity}")

        if cosine_similarity >= threshold:
            return True
        else:
            return False
            
    except Exception as e:
        return {
            "status": "Error",
            "message": f"Ensure Ollama app is running locally. Error: {str(e)}"
        }

def get_semantic_prompt(calendar_text, candidate_text):

	prompt = f"""
				You are a text comparison assistant. 
				Compare the between Calendar and CRM fields below and respond with ONLY a valid JSON object — no explanations, no markdown, no extra text.
				
				Calendar event:
				{calendar_text}

				CRM event:
				{candidate_text}

				Compare ONLY:
				- title sematically matching
				- description sematically matching

				if match then true else false.

				Return JSON only:

				{{
				    "matched": true/false,
				    "similarity_score": <number from 0 to 100>,
				    "reason": "..."
				}}
			"""

	return prompt



def reconcile_events(couch:CouchDBClient, event_type:str, embeddings:OllamaEmbeddings, llm:ChatOllama, vector_store:Chroma, parsing_callback_func):

	try:

		similarity_threshold = 0.80

		reconciled_data = []

		recon_log = []

		events = couch.find_by_attribute(attribute='type', value=event_type)

		for record in events:
			try:
				text, metadata = parsing_callback_func(record)
				results = vector_store.similarity_search_with_score(text, k=3)
				print(record['event_id'])
				logging.info(f"Calendar event {record['event_id']}")
				crm_text_list = []
				vector_store_search_res_score = {res[0].metadata['crm_id']:res[1] for res in results}

				calendar_text = f"""Title: {metadata['title']} \n Description: {metadata['description']}"""

				for res in results:

					common_attendees = set(metadata['attendees'].split(",")).intersection(set(res[0].metadata['attendees'].split(",")))
					logging.info(f"Common attendees {common_attendees}")
					logging.info(f"Calendar Event attendees {metadata['attendees']}")					
					logging.info(f"CRM Event attendees {res[0].metadata['attendees']}")
					logging.info(f"CRM Event date and time {res[0].metadata['meeting_date']} and {res[0].metadata['meeting_time']}")

					if metadata['date'] == res[0].metadata['meeting_date'] and metadata['time'] == res[0].metadata['meeting_time'] and len(common_attendees) >= 1:
						logging.info("Date and Time are exactly matching with one common attendees, no need to verify with llm.")
						print(res[0].metadata['crm_id'], res[1])
						print()

						crm_text_list.append(f"{res[0].metadata['crm_id']}\n\t\t{res[0].page_content}")

						crm_text = "\n\n".join(crm_text_list)

						prompt = get_semantic_prompt(calendar_text=text, candidate_text=crm_text)

						logging.info(f"Prompt for calendar event {metadata['event_id']} \n")
						logging.info(f"{prompt}")
						logging.info(f"Prompt \n ")

						response = llm.invoke(prompt)
						print(response.model_dump())
						model_response = response.model_dump()

						success = compare_texts(embeddings, calendar_text, crm_text, similarity_threshold)

						if success:

							# update recon status of calendar event
							couch.update(document_id=metadata['event_id'], data={'reconciled_event':True})
							# update recon status of crm event
							couch.update(document_id=res[0].metadata['crm_id'], data={'reconciled_event':True})

							result_data = {'type': 'vector_match',
											'event_id': record['event_id'],
											'response_content': model_response,
											'vector_res_score': vector_store_search_res_score}

							recon_log.append(result_data)

							reconciled_record_id = f"REC-{res[0].metadata['crm_id']}"

							reconciled_record = res[0].metadata
							reconciled_record['type'] = 'reconciled_crm_event'
							reconciled_record['event_id'] = record['event_id']
							reconciled_record['difference'] = model_response['reason']
							
							if not couch.exists(reconciled_record_id):
								reconciled_record['_id'] = reconciled_record_id
								couch.create(reconciled_record)
								logging.info(f"Reconciled record created {reconciled_record_id}")
							else:
								couch.update(reconciled_record_id, reconciled_record)
								logging.info(f"Reconciled record updated {reconciled_record_id} ")

						break

			except Exception as exp:
				logging.error(f"Error for record {record}")
				logger.exception(f"Error for record id : {record['event_id']}")

		couch.create({'type':'reconciliation', 'recon_log':recon_log})

	except FileNotFoundError:
		logging.error("Error: The file was not found.")
	except JSONDecodeError as e:
		logging.error(f"Error: Invalid JSON formatting (Line {e.lineno}, Column {e.colno}).")


if __name__ == "__main__":

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

	cwd = os.getcwd()
	
	ollama_url = os.getenv("OLLAMA_BASE_URL","http://localhost:11434")

	embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

	vector_store = Chroma(
			collection_name="meetings",
			embedding_function=embeddings,
		    persist_directory=f"{cwd}/chroma_langchain_db"
		)

	llm = ChatOllama(
			model = 'qwen2.5:1.5b',
			temperature = 0.5,
			base_url=ollama_url,
		    model_kwargs = {
		        "num_ctx": 2048,       # Limits context so old tokens are forcefully dropped
		        "repeat_penalty": 1.2,  # Prevents the model from repeating its own/past output
		    }
		)

	structured_llm = llm.with_structured_output(MatchResult)

	filepath = f"{cwd}/data/calendar_events.json"

	reconcile_events(couch, 'calendar_event', embeddings, structured_llm, vector_store, Utils.parse_and_normalise_calendar_event)
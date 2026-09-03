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
from json import JSONDecodeError
from utils import Utils


# Configure logging settings
logging.basicConfig(
    filename='reconcile_app.log',
    filemode='a', # 'a' to append, 'w' to overwrite each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO # Capture INFO, WARNING, ERROR, and CRITICAL logs
)

logger = logging.getLogger(__name__)

def get_semantic_prompt(calendar_text, candidate_text):

	prompt = f"""
				You are a meeting reconciliation system.

				Determine whether the calendar event matches any CRM event.

				Calendar event:
				{calendar_text}

				Candidate CRM events:
				{candidate_text}


				Compare ONLY:
				- title can be sematically matching
				- company can be sematically matching
				- attendees can be sematically matching
				- location can be sematically matching
				- description can be loose matching

				if any four compare match then true else false.

				Return JSON only:

				{{
				    "matched": true/false,
				    "crm_id": "...",
				    "confidence": 0.0,
				    "reason": "..."
				}}
			"""

	return prompt


def get_strict_prompt(calendar_text, candidate_text):

	prompt = f"""
				You are a meeting reconciliation system.

				Determine whether the calendar event matches any CRM event.

				Calendar event:
				{calendar_text}

				Candidate CRM events:
				{candidate_text}


				Compare:
				- title can be sematically matching
				- date should be strictly same
				- time should be strictly same
				- company can be sematically matching
				- attendees can be sematically matching
				- location can be sematically matching
				- description can be loose matching

				if any five compare match then matched is true else false.

				Return JSON only:

				{{
				    "matched": true/false,
				    "crm_id": "...",
				    "confidence": 0.0,
				    "reason": "..."
				}}
			"""

	return prompt


def reconcile_events(couch:CouchDBClient, event_type:str, llm:ChatOllama, vector_store:Chroma, parsing_callback_func):

	try:

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
				confirm_with_llm = True
				reconciled_status = False

				for res in results:

					common_attendees = set(metadata['attendees'].split(",")).intersection(set(res[0].metadata['attendees'].split(",")))
					logging.info(f"Common attendees {common_attendees}")
					if metadata['date'] == res[0].metadata['date'] and metadata['time'] == res[0].metadata['time'] and len(common_attendees) >= 2:
						logging.info("Date and Time are exactly matching with two common attendees, no need to verify with llm.")
						print(res[0].metadata['crm_id'], res[1])
						print()


						crm_text_list.append(f"{res[0].metadata['crm_id']}\n\t\t{res[0].page_content}")
						print(res[0].metadata['crm_id'], res[1])
						print()

						crm_text = "\n\n".join(crm_text_list)
						# logging.info(f"Crm text Content \n {crm_text}")

						prompt = get_semantic_prompt(calendar_text=text, candidate_text=crm_text)

						logging.info(f"Prompt for calendar event {metadata['event_id']} \n")
						logging.info(f"{prompt}")
						logging.info(f"Prompt \n ")

						response = llm.invoke(prompt)
						print(response.content)
						logging.info(f"Calendar event {record['event_id']}")

						confirm_with_llm = False
						reconciled_status = True
						# update recon status of calendar event
						couch.update(document_id=metadata['event_id'], data={'reconciled_event':True})
						# update recon status of crm event
						couch.update(document_id=res[0].metadata['crm_id'], data={'reconciled_event':True})

						result_data = {'type': 'vector_match',
										'event_id': record['event_id'],
										'response_content': json.loads(response.content),
										'vector_res_score': vector_store_search_res_score}

						recon_log.append(result_data)

				if reconciled_status:
					reconciled_record = metadata	
					reconciled_record['type'] = 'reconciled_event'
					reconciled_record['_id'] = f"REC-{record['event_id']}" 
					logging.info("Creating reconciled_record")
					logging.info(f"Reconciled record {reconciled_record}")
					couch.create(reconciled_record)
					logging.info("Created reconciled_record")

				# No match found give all data to llm to decide.
				if confirm_with_llm:
					for res in results:
						crm_text_list.append(f"{res[0].metadata['crm_id']}\n\t\t{res[0].page_content}")
						print(res[0].metadata['crm_id'], res[1])
						print()

					crm_text = "\n\n".join(crm_text_list)
					# logging.info(f"Crm text Content \n {crm_text}")

					prompt = get_strict_prompt(calendar_text=text, candidate_text=crm_text)

					logging.info(f"Prompt for calendar event {metadata['event_id']} \n")
					logging.info(f"{prompt}")
					logging.info(f"Prompt \n ")

					response = llm.invoke(prompt)
					print(response.content)
					logging.info(f"Calendar event {record['event_id']}")

					event_id = record['event_id']
					result_data = {'type': 'llm_confirm',
									'event_id': event_id,
									'response_content': json.loads(response.content), 
									'vector_res_score': vector_store_search_res_score}

					recon_log.append(result_data)

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
	    url="http://localhost:5984/",
	    username="admin",
	    password="password",
	    database="assessment"
	)

	couch.connect()

	cwd = os.getcwd()
	
	embeddings = OllamaEmbeddings(model="nomic-embed-text")

	vector_store = Chroma(
			collection_name="meetings",
			embedding_function=embeddings,
		    persist_directory=f"{cwd}/chroma_langchain_db"
		)

	llm = ChatOllama(
			model='qwen2.5:1.5b',
			temperature=0.5
		)

	filepath = f"{cwd}/data/calendar_events.json"

	reconcile_events(couch, 'calendar_event', llm, vector_store, Utils.parse_and_normalise_calendar_event)
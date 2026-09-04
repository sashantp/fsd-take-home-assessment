import os
import json
import logging
import re

from datetime import datetime
from json import JSONDecodeError
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path


class Utils():

	@staticmethod
	def split_email(email:str)-> tuple[str,str]:

			pattern = r"@|\[at\]"
			splitted = re.split(pattern, email)
			logging.debug(f"Splitted email {email} to {splitted}")
			if len(splitted) == 2:
				return splitted[0], splitted[1]
			return splitted[0], None

	@staticmethod
	def parse_and_normalise_calendar_event(record: dict)-> (str,dict):
		
		start_dt_obj = datetime.fromisoformat(record['start_time'])
		end_dt_obj = datetime.fromisoformat(record['start_time'])

		organizer_name, organizer_company = Utils.split_email(record['organizer'])

		clients = set()
		attendees = []

		for attendee in record['attendees']:
			if not organizer_company in attendee:
				clients.add(attendee)
			else:
				name, domain = Utils.split_email(attendee)
				attendees.append(" ".join([val.capitalize() for val in name.split(".")]))					
		
		companies = set()
		if clients:
			for c in clients:
				name, domain = Utils.split_email(c)
				if name:
					attendees.append(" ".join([val.capitalize() for val in name.split(".")]))
				if domain:
					domain_split = domain.split(".")
					if len(domain_split) > 0:
						companies.add(domain_split[0].capitalize())
		
		date = start_dt_obj.strftime("%Y-%m-%d")
		time = start_dt_obj.strftime("%H:%M")

		calendar_text = f"""
				Title: {record['title']}
				Client: {", ".join(companies) if companies else None}
				Attendees: {", ".join(attendees)}
				Date: {date}
				Time: {time}
				Location: {record['location']}
				Description: {record['description']}
		"""

		metadata = record
		metadata['source'] = "calendar"
		metadata['record_type'] = "calendar_event"
		metadata['attendees'] = ",".join(attendees)
		metadata['date'] = date
		metadata['time'] = time

		del metadata['reconciled_event']

		logging.info(f"Parsed and normalised calendar event")
		logging.info(f"Parsed calendar event text {calendar_text}")
		logging.info(f"Parsed calendar event metadata {metadata}")

		return calendar_text, metadata

	@staticmethod
	def parse_and_normalise_crm_event(record: dict)-> (str,dict):

		attendees = []

		if record['client_name']:
			attendees.append(record['client_name'])

		if record['relationship_owner']:
			attendees.append(record['relationship_owner'])

		record['meeting_date'] = record['meeting_date'] if record['meeting_date'] else ''
		record['meeting_time'] = record['meeting_time'] if record['meeting_time'] else ''

		crm_text = f"""
		Title: {record['subject']}
		Client: {record['client_company']}
		Attendees: {", ".join(attendees)}
		Date: {record['meeting_date']}
		Time: {record['meeting_time']}
		Location: {record['location']}
		Description: {record['notes']}
		"""

		metadata = record
		metadata['source'] = "crm"
		metadata['record_type'] = "crm_meeting"
		metadata['attendees'] = ",".join(attendees)

		del metadata['reconciled_event']

		logging.info(f"Parsed and normalised crm event")
		logging.info(f"Parsed crm event text {crm_text}")
		logging.info(f"Parsed crm event metadata {metadata} \n")

		return crm_text, metadata

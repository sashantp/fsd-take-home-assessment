# Assessment

**Event Sync Service** for a small internal platform


## 🛠️ Built With
- [Python/LangChain](https://www.langchain.com/)
- [CouchDB](https://couchdb.apache.org/)

## 📦 Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.12.0+
- Docker
- Install [Ollama](https://docs.ollama.com/linux)
- Install [pyenv](https://github.com/pyenv/pyenv) 


## ⚙️ Installation & Setup
Follow these steps to get your development environment running:


1. Run docker compose build (for first time): 
   ```bash
	docker compose -f docker-compose.yml build
   ```

2. Run docker compose up: 
   ```bash
	docker compose -f docker-compose.yml up -d
   ```

3. View Front-End Pages.

- [Calender Events](http://127.0.0.1:5173/calender)
- [CRM Events](http://127.0.0.1:5173/crm/)
- [CRM Events Reconciled](http://127.0.0.1:5173/crm/reconciled)


4. Stop and remove all the containers once done:
   ```bash
   docker compose -f docker-compose.yml down
   ```

5. Delete couchdb volume once done:
   ```bash
   docker volume rm fsd-take-home-assessment_couchdb_data
   ```


## Front-End Pages.

- [Calender Events](http://127.0.0.1:5173/calender)
- [CRM Events](http://127.0.0.1:5173/crm/)
- [CRM Events Reconciled](http://127.0.0.1:5173/crm/reconciled)

## FastAPI endpoints.

- http://127.0.0.1:8000/events/crm
- http://127.0.0.1:8000/events/calendar
- http://127.0.0.1:8000/events/crm/reconciled

## CouchDB

- http://localhost:5984/_utils/#login
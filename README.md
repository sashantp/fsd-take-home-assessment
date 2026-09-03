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

1. Create virtual environment: 
   ```bash
	pyenv virtualenv 3.12.10 assessment
   ```

2. Activate virtual environment: 
   ```bash
	pyenv activate assessment
   ```

3. Install all the python packages from requirements.txt: 
   ```bash
	pip install -r requirements.txt
   ```

4. Clone the repository:
   ```bash
   git clone https://github.com
   ```

5. Pull Ollama model:
   ```bash
   ollama pull nomic-embed-text:latest
   ollama pull qwen2.5:1.5b
   ```

6. Run docker compose build (for first time): 
   ```bash
	docker compose -f docker-compose.yml build
   ```

7. Run docker compose up: 
   ```bash
	docker compose -f docker-compose.yml up -d
   ```

8. Run Data ingestion service:
   ```bash
	python data_ingestion_service.py
   ```

9. Run to create vector database:
   ```bash
	python build_vector_db.py
   ```

10. Run reconciliation service:
   ```bash
	python reconciliation_service.py
   ```

11. To delete setup once everything is complete:
   ```bash
	python destroy.py
   ```

12. Stop docker compose up: 
   ```bash
	docker compose -f docker-compose.yml down
   ```


## Front-End Pages.

- [Calender Events](http://127.0.0.1:5173/calender)
- [CRM Events](http://127.0.0.1:5173/crm/)
- [CRM Events Reconciled](http://127.0.0.1:5173/crm/reconciled)

## FastAPI endpoints.

- http://127.0.0.1:8000/events/crm
- http://127.0.0.1:8000/events/calendar
- http://127.0.0.1:8000/events/crm/reconciled
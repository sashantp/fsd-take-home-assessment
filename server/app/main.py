from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from couch_db_client import CouchDBClient
from dependencies import couchdb_client, get_couchdb


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://172.19.0.3:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    couchdb_client.connect()


@app.get("/")
def read_root():
  return {"message": "Hello World"}


@app.get("/events/crm")
def crm_events(db: CouchDBClient = Depends(get_couchdb)):

  events = db.find_by_attribute(attribute='type', value='crm_event')

  if events is None:
    raise HTTPException(status_code=404, detail="Record not found")

  return events


@app.get("/events/calendar")
def calendar_events(db: CouchDBClient = Depends(get_couchdb)):

  events = db.find_by_attribute(attribute='type', value='calendar_event')

  if events is None:
    raise HTTPException(status_code=404, detail="Record not found")

  return events


@app.get("/events/crm/reconciled")
def calendar_events(db: CouchDBClient = Depends(get_couchdb)):

  events = db.find_by_attribute(attribute='type', value='reconciled_crm_event')

  if events is None:
    raise HTTPException(status_code=404, detail="Record not found")

  return events


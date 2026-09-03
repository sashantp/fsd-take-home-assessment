from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from couch_db_client import CouchDBClient
from dependencies import couchdb_client, get_couchdb


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

  record = db.get('crm_events')

  if record is None:
    raise HTTPException(status_code=404, detail="Record not found")

  return record.get("events", {})


@app.get("/events/calendar")
def calendar_events(db: CouchDBClient = Depends(get_couchdb)):

  record = db.get('calendar_events')

  if record is None:
    raise HTTPException(status_code=404, detail="Record not found")

  return record.get("events", {})



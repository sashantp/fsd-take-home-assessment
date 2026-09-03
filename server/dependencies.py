import os

from couch_db_client import CouchDBClient


couchdb_client = CouchDBClient(
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


def get_couchdb() -> CouchDBClient:
    return couchdb_client
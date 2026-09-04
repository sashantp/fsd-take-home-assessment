import couchdb
from typing import Optional, Dict, Any


class CouchDBClient:
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        database: str
    ):
        self.url = url
        self.username = username
        self.password = password
        self.database_name = database

        self.server = None
        self.db = None

    def connect(self):
        """Connect to CouchDB and select/create database."""

        self.server = couchdb.Server(self.url)

        # Authenticate
        self.server.resource.credentials = (
            self.username,
            self.password
        )

        # Create database if it doesn't exist
        if self.database_name in self.server:
            self.db = self.server[self.database_name]
        else:
            self.db = self.server.create(self.database_name)

        return self.db

    def close(self):
        """Close connection."""
        self.server = None
        self.db = None

    def create(self, document: Dict[str, Any]) -> str:
        """Create a document."""
        if self.db is None:
            raise RuntimeError("Database is not connected")

        doc_id, doc = self.db.save(document)
        return doc_id

    def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        if self.db is None:
            raise RuntimeError("Database is not connected")

        if document_id in self.db:
            return self.db[document_id]

        return None

    def update(
        self,
        document_id: str,
        data: Dict[str, Any]
    ) -> str:
        """Update an existing document."""

        if self.db is None:
            raise RuntimeError("Database is not connected")

        if document_id not in self.db:
            raise KeyError(
                f"Document {document_id} does not exist"
            )

        document = self.db[document_id]
        document.update(data)

        doc_id, _ = self.db.save(document)

        return doc_id

    def delete(self, document_id: str):
        """Delete a document."""

        if self.db is None:
            raise RuntimeError("Database is not connected")

        if document_id not in self.db:
            raise KeyError(
                f"Document {document_id} does not exist"
            )

        document = self.db[document_id]
        self.db.delete(document)

    def exists(self, document_id: str) -> bool:
        """Check whether document exists."""
        return (
            self.db is not None
            and document_id in self.db
        )

    def find_by_attribute(self, attribute:str, value):

        result = self.db.find({'selector': {attribute:value}})

        return list(result)
from typing import Optional
from .database import Database
import base64
import gzip
import json
import pickle
import pyrebase


class FirebaseDatabase(Database):
    def __init__(self, serialised_config: str):
        self.config = pickle.loads(
            gzip.decompress(base64.b64decode(serialised_config)))

    def add_document(self, id: str, doc: dict) -> None:
        self._upload_analysis(id, doc)

    def get_document_as_str(self, id: str) -> Optional[str]:
        return self._fetch_analysis_data(id)

    def _open_db_connection(self):
        return pyrebase.initialize_app(self.config).database()

    def _upload_analysis(self, replay_id: str, replay_analysis: dict) -> None:
        db = self._open_db_connection()
        db.child("inject_analyses").child(replay_id).set(
            json.dumps(replay_analysis))

    def _fetch_analysis_data(self, replay_id: str) -> str:
        db = self._open_db_connection()
        analysis_data = db.child("inject_analyses").child(
            replay_id).get().val()
        return analysis_data if analysis_data else ""

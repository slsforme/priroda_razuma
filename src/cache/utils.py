from fastapi_cache.coder import Coder

from typing import Any
import base64
import json

class Base64Coder(Coder):
    @classmethod
    def encode(cls, value: Any) -> str:
        if isinstance(value, bytes):
            return base64.b64encode(value).decode('utf-8')
        return json.dumps(value, default=str).encode('utf-8')

    @classmethod
    def decode(cls, value: bytes) -> Any:
        try:
            return base64.b64decode(value)
        except:
            return json.loads(value.decode('utf-8'))
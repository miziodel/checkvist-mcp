import json
from typing import Any, Optional

class StandardResponse:
    @staticmethod
    def success(message: str, data: Any = None) -> str:
        payload = {
            "success": True,
            "message": message
        }
        if data is not None:
            payload["data"] = data
        return json.dumps(payload, indent=2)

    @staticmethod
    def error(message: str, action: str, next_steps: str, error_details: Optional[str] = None) -> str:
        payload = {
            "success": False,
            "message": message,
            "action": action,
            "next_steps": next_steps
        }
        if error_details:
            payload["error_details"] = error_details
        return json.dumps(payload, indent=2)

import json
from typing import Any, Optional, Union
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    suggestion: Optional[str] = None
    action: Optional[str] = None
    error_details: Optional[str] = None

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
    def error(message: str, error_code: str, strategy: str = None, action: str = None, error_details: Optional[str] = None) -> str:
        """
        [BREAKING v1.3] Standardized error format.
        error_code: E001 (Auth), E002 (Found), E003 (Rate), E004 (Internal)
        strategy: Replaced 'next_steps' with suggestion-driven strategy.
        """
        payload = ErrorResponse(
            error_code=error_code,
            message=message,
            suggestion=strategy,
            action=action,
            error_details=error_details
        )
        return payload.model_dump_json(indent=2)

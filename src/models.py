from pydantic import BaseModel, Field, field_validator, AliasChoices
from typing import List, Optional, Any, Dict, Set

class Task(BaseModel):
    id: int
    content: str
    parent_id: Optional[int] = None
    checklist_id: Optional[int] = Field(None, validation_alias=AliasChoices("checklist_id", "list_id"))
    # Multi-alias for compatibility across different JSON responders
    list_id: Optional[int] = Field(None, alias="list_id")
    priority: Optional[int] = Field(0, validation_alias=AliasChoices("priority", "mark"))
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[str] = Field(None, validation_alias=AliasChoices("due_date", "due"))
    status: int = 0 # 0 = open, 1 = closed
    notes_count: int = 0
    comments_count: int = 0
    has_notes: Optional[bool] = None
    has_comments: Optional[bool] = None

    @field_validator('has_notes', 'has_comments', mode='before')
    @classmethod
    def set_indicators(cls, v: Any, info: Any) -> Optional[bool]:
        if v is not None: return v
        # Best effort if v is None, we look at other fields in model_post_init or similar?
        # Actually field_validator mode='before' is better if we have the whole dict
        return v
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if self.has_notes is None:
            self.has_notes = self.notes_count > 0 or bool(self.notes)
        if self.has_comments is None:
            self.has_comments = self.comments_count > 0 or (bool(self.comments) and len(self.comments) > 0)
    
    notes: Optional[str] = None
    comments: List[dict] = Field(default_factory=list) # Simplification to avoid rebuild for now
    updated_at: Optional[str] = None

    @field_validator('priority', mode='before')
    @classmethod
    def parse_priority(cls, v: Any) -> int:
        if v is None: return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    @field_validator('notes', mode='before')
    @classmethod
    def parse_notes(cls, v: Any) -> Optional[str]:
        if v is None: return None
        if isinstance(v, list):
            # API sometimes returns empty list [] for no notes
            if not v: return None
            # If it's a list of something, we probably want to join or just take first? 
            # Usually notes is a string per item in Checkvist.
            return str(v[0]) if len(v) > 0 else None
        return str(v)

    @field_validator('comments', mode='before')
    @classmethod
    def parse_comments(cls, v: Any) -> List[dict]:
        if isinstance(v, list):
            return v
        return []

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v: Any) -> List[str]:
        if isinstance(v, list):
            return [str(t) for t in v]
        if isinstance(v, dict):
            return [str(t) for t in v.keys()]
        if isinstance(v, str):
            if not v.strip(): return []
            return [t.strip() for t in v.split(',') if t.strip()]
        return []

class Checklist(BaseModel):
    id: int
    name: str
    public: bool = False

class Comment(BaseModel):
    id: int
    comment: str
    user_name: Optional[str] = None
    updated_at: Optional[str] = None

import pytest
from src.models import Task, Checklist, Comment

def test_task_model_validation():
    # Min valid task
    t = Task(id=1, content="Task")
    assert t.id == 1
    assert t.content == "Task"
    assert t.tags == []
    
    # Full task
    data = {
        "id": 101,
        "content": "Full Task",
        "parent_id": 1,
        "priority": 1,
        "tags": ["work", "urgent"],
        "due_date": "2024-12-31",
        "status": 0
    }
    t = Task(**data)
    assert t.priority == 1
    assert "work" in t.tags

def test_checklist_model():
    cl = Checklist(id=10, name="List")
    assert cl.public is False
    
    cl2 = Checklist(id=11, name="Public", public=True)
    assert cl2.public is True

def test_comment_model():
    c = Comment(id=1, comment="Hello")
    assert c.id == 1
    assert c.user_name is None

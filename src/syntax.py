import re
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass, field

@dataclass
class ParseResult:
    content: str
    tags: Set[str] = field(default_factory=set)
    priority: int = 0
    due: Optional[str] = None
    user: Optional[str] = None

class SyntaxParser:
    """
    Utility to parse Checkvist smart syntax from strings.
    Supports: #tag, !priority, ^date, @user
    """
    
    TAG_REGEX = r'#(\w+)'
    PRIORITY_REGEX = r'!+([1-3])'
    DUE_REGEX = r'\^([^\s]+)'
    USER_REGEX = r'@([^\s]+)'
    LINK_REGEX = r'\[(?:id:)?([^\]]+)\](?:\((.*?)\))?'

    def extract_tags(self, text: str) -> Tuple[str, Set[str]]:
        tags = set(re.findall(self.TAG_REGEX, text))
        clean_text = re.sub(self.TAG_REGEX, '', text).strip()
        # Clean up double spaces that might result from removal
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text, tags

    def extract_priority(self, text: str) -> Tuple[str, int]:
        matches = re.findall(self.PRIORITY_REGEX, text)
        priority = int(matches[0]) if matches else 0
        clean_text = re.sub(self.PRIORITY_REGEX, '', text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text, priority

    def extract_due_date(self, text: str) -> Tuple[str, Optional[str]]:
        matches = re.findall(self.DUE_REGEX, text)
        due = matches[0] if matches else None
        clean_text = re.sub(self.DUE_REGEX, '', text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text, due

    def extract_user(self, text: str) -> Tuple[str, Optional[str]]:
        matches = re.findall(self.USER_REGEX, text)
        user = matches[0] if matches else None
        clean_text = re.sub(self.USER_REGEX, '', text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text, user

    def parse(self, text: str) -> ParseResult:
        """Fully parse a string and return a ParseResult object."""
        current_text = text
        # Order matters for progressive cleaning
        
        # Pre-process shorthands
        current_text = current_text.replace("!!1", "!1")
        
        current_text, tags = self.extract_tags(current_text)
        current_text, priority = self.extract_priority(current_text)
        current_text, due = self.extract_due_date(current_text)
        current_text, user = self.extract_user(current_text)
        
        return ParseResult(
            content=current_text.strip(),
            tags=tags,
            priority=priority,
            due=due,
            user=user
        )

    def has_symbols(self, text: str) -> bool:
        """Check if the text contains any smart syntax symbols."""
        # Using self.__class__ for absolute safety or direct attribute access
        regexes = [self.TAG_REGEX, self.PRIORITY_REGEX, self.DUE_REGEX, self.USER_REGEX, self.LINK_REGEX]
        for regex in regexes:
            if re.search(regex, text):
                return True
        return False

import logging
import re

class SecretMasker(logging.Filter):
    """
    A logging filter that masks sensitive Checkvist information.
    Specifically masks remote_key (API key) and X-Client-Token.
    """
    def filter(self, record):
        if not isinstance(record.msg, str):
            return True
        
        # Mask remote_key, X-Client-Token, and generic token with robust regex
        # Pattern: Key name + optional quotes + optional space + separator (: or =) + optional space + optional quotes + value
        mask_pattern = r'(X-Client-Token|remote_key|token)([\'"]?\s*[:=]\s*[\'"]?)([^&\s\'",}]*)'
        record.msg = re.sub(mask_pattern, r'\1\2[MASKED]', record.msg, flags=re.IGNORECASE)
        
        return True

def setup_logging(level=logging.INFO):
    # Configure the root logger for the 'src' package
    logger = logging.getLogger("src")
    
    # If we are running as a server, we might also want to catch mcp logs
    mcp_logger = logging.getLogger("mcp")
    
    masker = SecretMasker()
    
    for l in [logger, mcp_logger]:
        if not any(isinstance(f, SecretMasker) for f in l.filters):
            l.addFilter(masker)
            
    return logger

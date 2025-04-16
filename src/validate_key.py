import os
import re
from openai import OpenAI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_openai_key(api_key=None):
    """
    Validate an OpenAI API key.
    Returns: (bool, str) - (is_valid, message)
    """
    try:
        # Use provided key or environment variable
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        # Check if key is set
        if not api_key:
            return False, "OPENAI_API_KEY is not set"

        # Check for non-ASCII characters
        if not api_key.isascii():
            return False, "API key contains non-ASCII characters"

        # Check format (basic regex for OpenAI key: sk- followed by alphanumeric)
        if not re.match(r"^sk-[a-zA-Z0-9_-]+$", api_key):
            return False, "API key format invalid (expected sk- followed by alphanumeric characters)"

        # Test authentication with OpenAI
        client = OpenAI(api_key=api_key)
        # Make a minimal API call (e.g., list models)
        client.models.list()
        logger.info("API key validated successfully")
        return True, "API key is valid"
    
    except Exception as e:
        logger.error(f"API key validation failed: {e}")
        return False, f"API key validation failed: {str(e)}"

if __name__ == "__main__":
    # Test the key
    is_valid, message = validate_openai_key()
    print(f"Validation result: {message}")
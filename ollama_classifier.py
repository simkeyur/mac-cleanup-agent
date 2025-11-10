"""
Ollama Classifier Module
Uses Ollama to intelligently classify files with unknown types
"""
import logging
from pathlib import Path

try:
    import ollama
except ImportError:
    ollama = None

logger = logging.getLogger(__name__)


class OllamaClassifier:
    """Uses Ollama to classify files intelligently"""
    
    def __init__(self, config):
        if ollama is None:
            logger.warning("Ollama package not installed. AI classification disabled.")
            self.enabled = False
            return
        
        self.config = config
        self.enabled = True
        self.model = config['ollama']['model']
        self.temperature = config['ollama'].get('temperature', 0.3)
        self.timeout = config['ollama'].get('timeout', 30)
        self.base_url = config['ollama'].get('base_url', 'http://localhost:11434')
        
        # Categories from config
        self.categories = list(config['file_types'].keys()) + [config['organization']['misc_folder']]
        
        try:
            # Initialize Ollama client
            self.client = ollama.Client(host=self.base_url)
            logger.info(f"Ollama classifier initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            self.enabled = False
    
    def classify_file(self, file_path):
        """Classify a file using Ollama"""
        if not self.enabled:
            return None
        
        try:
            file_name = file_path.name
            file_ext = file_path.suffix.lower()
            
            # Build prompt for classification
            prompt = f"""You are a file classification assistant. Classify the following file into ONE category.

File name: {file_name}
File extension: {file_ext}

Available categories: {', '.join(self.categories)}

Respond with ONLY the category name, nothing else. If uncertain, respond with 'misc'.

Category:"""
            
            logger.debug(f"Classifying {file_name} with Ollama")
            
            # Call Ollama
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'num_predict': 20,  # Short response
                }
            )
            
            # Extract category from response
            category = response['response'].strip().lower()
            
            # Validate category
            if category in self.categories:
                logger.info(f"Ollama classified {file_name} as: {category}")
                return category
            else:
                logger.warning(f"Ollama returned invalid category '{category}' for {file_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error classifying {file_path} with Ollama: {e}")
            return None
    
    def is_available(self):
        """Check if Ollama is available and running"""
        if not self.enabled:
            return False
        
        try:
            # Try to list models to check if server is running
            self.client.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama server not available: {e}")
            return False

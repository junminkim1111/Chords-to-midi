class Config:

    # API_KEY = os.getenv("GEMINI_API_KEY")
    
    MODEL_NAME = "models/gemini-2.5-flash"

    base_file_path = "./midi/"
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    TIMEOUT_MS = 30000
    
    DEFAULT_BPM = 120
    DEFAULT_INSTRUMENT = 0 
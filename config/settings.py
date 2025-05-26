import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL_NAME = "nvidia/llama-3.3-nemotron-super-49b-v1"

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
MAX_ITERATIONS = 5
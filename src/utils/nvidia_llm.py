"""
NVIDIA NIM Client Module

This module provides a client for interacting with NVIDIA's NIM API using the OpenAI API format.
It allows for generating text completions using NVIDIA's Llama 3.3 Nemotron Super 49B model.
"""

from openai import OpenAI
from typing import List, Dict, Any
import json

class NvidiaNIMClient:
    """
    Client for interacting with NVIDIA's NIM API for LLM inference.
    
    This class wraps the OpenAI API client configured to use NVIDIA's endpoints
    and provides methods for text generation using NVIDIA's models.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://integrate.api.nvidia.com/v1"):
        """
        Initialize the NVIDIA NIM client.
        
        Args:
            api_key (str): API key for authentication with NVIDIA NIM API
            base_url (str, optional): Base URL for the NVIDIA NIM API. 
                                     Defaults to "https://integrate.api.nvidia.com/v1".
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1"  # Default model

    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.0, max_tokens: int = 1000) -> str:
        """
        Send a chat completion request to the NVIDIA NIM API.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            temperature (float, optional): Controls randomness in generation. Defaults to 0.0.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1000.
            
        Returns:
            str: The generated text response or error message
        """
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages= messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1.0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during chat completion: {e}")
            return f"Error: {str(e)}"
    
    def invoke(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Simplified method to invoke the model with a single prompt.
        
        Args:
            prompt (str): The text prompt to send to the model
            temperature (float, optional): Controls randomness in generation. Defaults to 0.0.
            
        Returns:
            str: The generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, temperature=temperature)
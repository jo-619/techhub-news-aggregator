import subprocess
import json
from typing import Dict, Optional

def summarize_with_ollama(text: str, model: str = "mistral") -> Dict[str, str]:
    """
    Summarize text using Ollama with a structured prompt
    Returns a dictionary with summary, key_points, and sentiment
    """
    if not text or len(text.strip()) < 50:
        return {
            "summary": "Text too short for meaningful summary",
            "key_points": [],
            "sentiment": "neutral",
            "error": None
        }
    
    # Truncate text if too long (Ollama has token limits)
    max_length = 4000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    prompt = f"""Please analyze the following news article and provide:

1. A concise summary (2-3 sentences)
2. Key points (3-5 bullet points)
3. Sentiment analysis (positive, negative, or neutral)

Article: {text}

Please respond in JSON format:
{{
    "summary": "Your summary here",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "sentiment": "positive/negative/neutral"
}}"""

    try:
        cmd = ["ollama", "run", model]
        proc = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = proc.communicate(input=prompt, timeout=60)
        
        if proc.returncode != 0:
            return {
                "summary": "Error: Failed to process with Ollama",
                "key_points": [],
                "sentiment": "neutral",
                "error": stderr
            }
        
        # Try to parse JSON response
        try:
            result = json.loads(stdout.strip())
            return {
                "summary": result.get("summary", "No summary generated"),
                "key_points": result.get("key_points", []),
                "sentiment": result.get("sentiment", "neutral"),
                "error": None
            }
        except json.JSONDecodeError:
            # If not JSON, return the raw text as summary
            return {
                "summary": stdout.strip(),
                "key_points": [],
                "sentiment": "neutral",
                "error": "Response not in JSON format"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "summary": "Error: Ollama request timed out",
            "key_points": [],
            "sentiment": "neutral",
            "error": "Timeout"
        }
    except FileNotFoundError:
        return {
            "summary": "Error: Ollama not found. Please install Ollama and the model.",
            "key_points": [],
            "sentiment": "neutral",
            "error": "Ollama not installed"
        }
    except Exception as e:
        return {
            "summary": f"Error: {str(e)}",
            "key_points": [],
            "sentiment": "neutral",
            "error": str(e)
        }

def get_simple_summary(text: str) -> str:
    """Get a simple text summary without structured output"""
    result = summarize_with_ollama(text)
    return result["summary"]

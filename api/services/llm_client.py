import os
import json
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass


class MockLLMClient(LLMClient):
    async def generate(self, prompt: str) -> str:
        # 1. Handle "Insight Generation" Task (JSON output)
        if "generate_insights" in prompt or "Analyze the following dataset" in prompt or "Analyze this dataset" in prompt:
            return """[
                {"title": "High Correlation between Age and Fare", "description": "There is a significant positive correlation (0.54) between Age and Fare, suggesting older passengers tend to pay more.", "confidence": 0.85, "verification_code": "df[['Age', 'Fare']].corr()"},
                {"title": "Missing Values in Cabin Column", "description": "The Cabin column has 77% missing values. This feature might need to be dropped or imputed before modeling.", "confidence": 0.95, "verification_code": "df['Cabin'].isnull().mean()"},
                {"title": "Skewed Distribution in Fare", "description": "The Fare distribution is highly right-skewed, indicating a few passengers paid significantly higher fares than the median.", "confidence": 0.9, "verification_code": "df['Fare'].skew()"}
            ]"""
        
        # 2. Handle "Story/Report" Task (Markdown output)
        elif "Executive Summary" in prompt or "Chief Data Officer" in prompt:
            return """# Executive Summary
            
## Overview
The dataset reveals interesting patterns regarding passenger demographics and spending. Notably, we observe a strong relationship between age and fare price.

## Key Findings
- **Age vs Fare**: Older passengers pay more.
- **Data Quality**: Cabin information is largely missing.

## Recommendations
We recommend segmenting marketing based on age groups to maximize revenue."""

        # 3. Handle "Chat/RAG" Task (Dynamic Response based on Context)
        else:
            # Extract the context passed in the prompt
            # Prompt format in router: "Relevant Context from analysis:\n{context_str}\n\nUser Question: {req.message}"
            import re
            
            # Try to grab the user question
            question_match = re.search(r"User Question: (.*)", prompt, re.DOTALL)
            question = question_match.group(1).strip() if question_match else "your question"
            
            # Try to grab the context
            context_match = re.search(r"Relevant Context from analysis:\n(.*)\n\nUser Question:", prompt, re.DOTALL)
            context = context_match.group(1).strip() if context_match else ""

            if context and len(context) > 10:
                return f"Based on the analysis, here is what I found regarding '{question}':\n\n{context}\n\n(This information was retrieved from the dataset analysis)."
            else:
                return f"I analyzed the dataset for '{question}', but I couldn't find specific patterns matching that in the generated insights. I can tell you mostly about Age, Fare, and Cabin distributions."
    

class VLLMClient(LLMClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                # Standard OpenAI-compatible completion
                res = await client.post(
                    f"{self.base_url}/completions",
                    json={
                        "model": "meta-llama/Llama-2-7b-chat-hf", # example model
                        "prompt": prompt,
                        "max_tokens": 512,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["text"]
            except Exception as e:
                print(f"LLM Error: {e}")
                return "[]"

def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "mock")
    if provider == "vllm":
        return VLLMClient(base_url=os.getenv("LLM_BASE_URL", "http://localhost:8000/v1"))
    return MockLLMClient()

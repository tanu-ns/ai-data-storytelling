import json
from ..services.llm_client import get_llm_client

async def generate_insights(dataset_profile: dict) -> list:
    """
    Uses the LLM to generate insights from the dataset profile.
    """
    client = get_llm_client()
    
    # Construct Prompt
    # We truncate summary to avoid context window issues in simple implementations
    summary_str = json.dumps(dataset_profile.get("summary", {}), indent=2)
    corr_str = json.dumps(dataset_profile.get("correlation", {}), indent=2)
    
    prompt = f"""
    You are an expert Data Analyst. Analyze the following dataset summary and correlation matrix.
    
    Summary Stats:
    {summary_str}
    
    Correlation Matrix:
    {corr_str}
    
    Provide 3 distinct, interesting business or data quality insights.
    Return the response as a valid JSON array of objects with keys: "title", "description", "confidence" (0-1), "verification_code" (pandas/python).
    Do not output any markdown formatting, just the raw JSON string.
    """
    
    # Call LLM
    response_text = await client.generate(prompt)
    
    # Parse Response
    try:
        # improved cleanup in case LLM is chatty
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text.replace("```json", "").replace("```", "")
        
        insights = json.loads(cleaned_text)
        return insights
    except json.JSONDecodeError:
        print(f"Failed to parse LLM response: {response_text}")
        return []

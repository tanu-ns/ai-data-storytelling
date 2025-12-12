from ..services.llm_client import get_llm_client
import json

async def generate_story(dataset_name: str, insights: list) -> str:
    """
    Generates a narrative data story based on the insights.
    """
    client = get_llm_client()
    
    # Mock Override for Demo (if using Mock Client, we return a fixed story to match the mock insights)
    # Ideally the MockLLMClient would handle this context-switching, but for simplicity:
    if "MockLLMClient" in str(type(client)):
        return f"""
# Executive Summary: {dataset_name}

## Key Findings
Analysis of the uploaded dataset reveals several critical trends. notably, there is a strong correlation between **Age and Fare** (0.54), suggesting that older demographic groups are driving higher revenue per ticket. This presents an opportunity to tailor premium services to this segment.

## Data Quality Concerns
However, data quality remains a challenge. The **Cabin** column has significant missing values (77%), which limits our ability to analyze location-based preferences. We recommend improving data collection at the point of booking.

## Pricing Strategy
The distribution of **Fares** is highly skewed. A small number of high-value transactions are distorting the average, indicating that a tiered pricing strategy might be more effective than a one-size-fits-all approach.
        """

    # Real LLM Prompt
    insights_str = "\n".join([f"- {i['title']}: {i['description']} (Conf: {i['confidence']})" for i in insights])
    
    prompt = f"""
    You are a Chief Data Officer writing an executive summary for a new dataset report: "{dataset_name}".
    
    Here are the key automated insights discovered:
    {insights_str}
    
    Write a 3-paragraph executive summary in Markdown format.
    - Paragraph 1: Overview and most critical finding.
    - Paragraph 2: Secondary findings and data quality notes.
    - Paragraph 3: Strategic recommendations based on the data.
    
    Use bolding for key terms. Do not include a greeting or sign-off.
    """
    
    response = await client.generate(prompt)
    return response

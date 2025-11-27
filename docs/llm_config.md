# LLM Configuration (Primary Model: mistral-7b-instruct)

## Provider: OpenRouter
- Base URL: https://openrouter.ai/api/v1/chat/completions
- API Key Required: Yes
- Model Used: mistral-7b-instruct
- Pricing: Free tier available
- Reason for Choice:
  - Good reasoning ability
  - Fast response time
  - High-quality instruction tuning
  - Ideal for structured career Q&A

## Authentication
Headers required for each request:

Authorization: Bearer <OPENROUTER_API_KEY>  
HTTP-Referer: http://localhost  
X-Title: StudentCareerChatbot  

## Example Request (Python)

POST https://openrouter.ai/api/v1/chat/completions

Body:
{
  "model": "mistral-7b-instruct",
  "messages": [
    {"role": "user", "content": "Example user query"}
  ]
}

## Fallback Plan
If OpenRouter fails or rate limits are hit:
- Use templated rule-based responses
- Use dataset-driven responses (skills, roadmap, projects)
- Avoid dependency on LLM for critical functions

## Rate limits & quotas (notes)
- OpenRouter free-tier may have rate limits or hourly quotas. Monitor responses for HTTP 429 or 503.
- Our backend uses simple retry + exponential backoff (2 retries). In production, improve with queuing or throttling.
- Always store API keys in environment variables. Do NOT commit API keys or .env files.

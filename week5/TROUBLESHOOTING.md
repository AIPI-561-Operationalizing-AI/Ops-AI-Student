# Week 5 Troubleshooting Guide

## Setup Issues

### API Key Not Found
**Error:** `ValueError: GOOGLE_API_KEY environment variable not set`

**Solution:**
1. Get free API key at https://aistudio.google.com/app/apikey
2. Set environment variable:
   ```bash
   export GOOGLE_API_KEY="your-key-here"
   ```
3. Or pass directly to Agent:
   ```python
   agent = Agent("data/techcorp.db", api_key="your-key-here")
   ```

### API Key Invalid
**Error:** `400 INVALID_ARGUMENT: API key not valid`

**Solution:**
- Verify key from https://aistudio.google.com/app/apikey
- Key should start with `AIza...`
- Check for extra spaces or line breaks in .env file
- Try generating a new key

### ModuleNotFoundError: google.genai
**Error:** `ModuleNotFoundError: No module named 'google.genai'`

**Solution:**
```bash
pip install --upgrade google-genai
```

## Runtime Issues

### Model Not Available
**Error:** `404 Requested entity was not found`

**Solution:**
- Verify you're using `gemini-2.5-pro` (or check available models)
- Try `gemini-1.5-flash` as fallback (faster, cheaper)
- Check https://ai.google.dev/ for current model availability

### Rate Limit Exceeded
**Error:** `429 Resource exhausted`

**Solution:**
- Free tier has request limits
- Wait 60 seconds before retrying
- Implement exponential backoff in your code:
  ```python
  import time
  for attempt in range(3):
      try:
          result = agent.query(question)
          return result
      except RateLimitError:
          if attempt < 2:
              time.sleep(2 ** attempt)
  ```

## Common Questions

**Q: Can I use a different LLM?**
A: Yes! Google GenAI SDK supports multiple models. Check https://ai.google.dev/ for current options. Update your Agent class to use a different model_id.

**Q: How do I track costs?**
A: Agent automatically calculates tokens → cost. Call `agent.get_metrics()` after queries to see totals.

**Q: Is there a maximum query size?**
A: Gemini 2.5 Pro supports ~100K tokens. Most enterprise queries are <2K tokens, so you're safe.

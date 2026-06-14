# Week 7 Troubleshooting Guide — Cost Optimization

## Common Issues

### Caching Not Working
**Issue:** Same query called twice still incurs cost twice

**Solution:**
- Verify cache key is correct (should be normalized query)
- Cache should store both question AND response
- Test caching:
  ```python
  optimizer = OptimizationStrategy()
  hit1, resp1 = optimizer.apply_caching("What is policy?", "Answer 1")
  hit2, resp2 = optimizer.apply_caching("What is policy?", "Answer 2")
  
  assert hit1 == False  # First call, not cached
  assert hit2 == True   # Second call, cached
  assert resp1 == resp2 # Same response
  ```

### Model Selection Not Reducing Cost
**Issue:** Expensive model still used for simple queries

**Solution:**
- Verify `select_model_by_complexity()` checks query length/keywords
- Simple queries should use gemini-1.5-flash (cheaper)
- Complex queries should use gemini-2.5-pro (stronger)
- Example implementation:
  ```python
  def select_model_by_complexity(self, query: str) -> str:
      # Simple heuristic: if query < 10 words, use flash
      if len(query.split()) < 10:
          return "gemini-1.5-flash"
      return "gemini-2.5-pro"
  ```

### Feedback Loop Not Saving Corrections
**Error:** `FeedbackLoop.submit_correction()` fails or doesn't store

**Solution:**
- Verify feedback is stored in `self.corrections` list
- Validate correction before storing:
  - corrected_answer must be longer than original (more detailed)
  - user_role must be in authority_hierarchy
- Test:
  ```python
  loop = FeedbackLoop()
  result = loop.submit_correction(
      "What is X?", "Wrong answer", "Correct and detailed answer", "manager"
  )
  assert result["accepted"] == True
  assert len(loop.corrections) == 1
  ```

### Cost Spike Detection Not Triggering
**Issue:** `identify_cost_spikes()` returns empty even with expensive query

**Solution:**
- Cost spike detection uses statistical threshold (mean + 2*std_dev)
- Need baseline of 10+ queries to establish normal distribution
- Test:
  ```python
  analyzer = CostAnalyzer()
  for i in range(10):
      analyzer.record_query({
        "query_text": f"query {i}",
        "retrieval_cost": 0.001,
        "llm_cost": 0.005,
        "tool_cost": 0.0,
        "error_cost": 0.0,
        "total_cost": 0.01,
        "timestamp": datetime.utcnow().isoformat()
    })
  analyzer.record_query({ # 100x more expensive
    "query_text": "expensive query",
    "retrieval_cost": 0.5,
    "llm_cost": 0.4,
    "tool_cost": 0.1,
    "error_cost": 0.0,
    "total_cost": 1.0,
    "timestamp": datetime.utcnow().isoformat()
  })

  spikes = analyzer.identify_cost_spikes()
  assert len(spikes) > 0
  ```

## Testing Issues

All code snippets below are reference implementations for methods in `cost_optimization_starter.py`.

### Test Fails: "apply_caching not implemented"
**Solution:**
- Implement caching with dict:
  ```python
  def apply_caching(self, query: str, response: str) -> tuple:
      if query in self.cache:
          return (True, self.cache[query])
      self.cache[query] = response
      return (False, response)
  ```

### Test Fails: "select_model_by_complexity"
**Solution:**
- Implement simple complexity check:
  ```python
  def select_model_by_complexity(self, query: str) -> str:
      complexity_words = ["analyze", "explain", "compare", "design"]
      if any(w in query.lower() for w in complexity_words):
          return "gemini-2.5-pro"
      return "gemini-1.5-flash"
  ```

### Feedback Validation Fails
**Solution:**
- Implement authority hierarchy:
  ```python
    def __init__(self):
      self.corrections = []
      self.authority = {
          "engineer": 1,
          "hr": 2,
          "finance": 2,
          "manager": 3,
          "executive": 4
      }
  
  def validate_correction(self, index: int) -> bool:
      correction = self.corrections[index]
      authority = self.authority.get(correction["user_role"], 0)
      # Need manager+ authority to accept corrections
      return authority >= 3 and len(correction["corrected_answer"]) > len(correction["original_answer"])
  ```

## Performance Issues

### Caching Wastes Memory
**Issue:** Cache grows indefinitely, memory usage increases

**Solution:**
- Implement LRU cache with max size:
  ```python
  from collections import OrderedDict
  
  # Optional enhancement: add max_cache_size parameter to limit memory usage
  class OptimizationStrategy:
      def __init__(self, max_cache_size=1000):
          self.cache = OrderedDict()
          self.max_cache_size = max_cache_size
      
      def apply_caching(self, query, response):
          if len(self.cache) > self.max_cache_size:
              self.cache.popitem(last=False)  # Remove oldest
          # ... rest of implementation
  ```

### Cost Analysis Too Slow
**Issue:** `get_cost_breakdown()` takes too long

**Solution:**
- Don't process entire history every time
- Cache summary statistics:
  ```python
  def __init__(self):
      self.query_history = []
      self._cached_breakdown = None
      self._last_update = 0
  
  def get_cost_breakdown(self):
      if self._cached_breakdown and len(self.query_history) == self._last_update:
          return self._cached_breakdown
      # Recalculate
      # ...
  ```

## Deployment Issues

### Feedback Loop Doesn't Persist
**Issue:** Corrections lost after restart

**Solution:**
- Save corrections to disk:
  ```python
  import json
  
  def save_corrections(self, path="data/corrections.json"):
      with open(path, 'w') as f:
          json.dump(self.corrections, f)
  
  def load_corrections(self, path="data/corrections.json"):
      with open(path, 'r') as f:
          self.corrections = json.load(f)
  ```

## FAQ

**Q: Should I optimize for cost or quality?**
A: Both. Use cheaper models where quality is acceptable (simple queries), expensive models where needed (complex reasoning). Measure both metrics.

**Q: How much cost can caching save?**
A: Depends on workload. If 50% of queries are repeats, caching saves 50%. Real-world: 20-40% savings.

**Q: Is feedback loop learning real?**
A: For this course: you're collecting corrections for analysis. In production, you'd retrain/fine-tune the model with corrections.

**Q: What if users submit wrong feedback?**
A: Validate feedback (length, authority level). Have humans review high-impact corrections before applying them.

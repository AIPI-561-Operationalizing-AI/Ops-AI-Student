# Week 6 Troubleshooting Guide — Access Control & Monitoring

## Common Issues

### Cost Enforcer Always Returns True
**Error:** `can_afford_query()` always returns True even when budget exceeded

**Solution:**
- Verify `add_cost()` is being called for every query
- Check that user_role matches a key in `role_budgets`
- Example:
  ```python
  enforcer = CostEnforcer()
  enforcer.add_cost("user1", "engineer", 50.0)
  enforcer.add_cost("user1", "engineer", 60.0)
  # Now total=110, engineer budget=100, so can_afford_query("user1", 10) = False
  ```

### Field Redaction Doesn't Work
**Error:** Sensitive fields not being redacted from responses

**Solution:**
- Verify field is listed in `sensitive_fields` in access_control.json
- Verify regex pattern is correct
- Test redaction:
  ```python
  controller = AccessController('data/access_control.json')
  response = 'Employee salary: $100,000'
  redacted = controller.redact_response("engineer", response)
  assert "salary" in redacted.lower() and "$100,000" not in redacted
  ```

### Audit Log Growing Too Large
**Issue:** Audit log list grows very large with many queries

**Solution:**
- Trim to recent entries periodically:
```python
  if len(controller.audit_log) > 10000:
      controller.audit_log = controller.audit_log[-5000:]  # Keep last 5000
```

## Performance Issues

### Rate Limiter Too Strict
**Issue:** `is_allowed()` returns False even with low traffic

**Solution:**
- Rate limiter measures per-minute
- If user hits limit at :59 seconds, they can't query again until 1 minute passes
- Increase `max_queries_per_minute` or implement sliding window

### Audit Logging Slows Down Queries
**Issue:** Every query call to `log_access()` is slow

**Solution:**
- For high-traffic systems, implement async logging:
  ```python
  import threading
  
  def log_access_async(self, ...):
      thread = threading.Thread(target=self.log_access, args=(role, resource, allowed, field))
      thread.daemon = True
      thread.start()
  ```

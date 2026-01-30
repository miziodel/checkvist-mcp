---
trigger: always_on
---

# 03 - MCP ROBUSTNESS & USABILITY

1. **MCP Ease of Use**: The server must be intuitive for LLM clients to consume. Tools should have clear docstrings and helpful error messages.
2. **Defensive Tooling**: Tools MUST perform explicit type casting (e.g., `int(val)`) for ID parameters received from the LLM. 
3. **Polymorphic Response Handling**: Tools MUST implement robust handling for non-deterministic API response formats (e.g., checking if a result is a `list` vs `dict`) before accessing specific keys.
4. **Organic Storage**: Checkvist must be treated as a fluid storage for notes and todos, not just a rigid database.

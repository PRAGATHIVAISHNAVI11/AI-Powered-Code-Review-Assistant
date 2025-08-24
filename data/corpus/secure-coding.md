# Secure Coding Snippets
- Validate and sanitize all inputs. Prefer allow-lists.
- Avoid eval, exec, and subprocess with unsanitized strings.
- Use parameterized SQL queries or ORM bindings.
- Secrets belong in env vars or secret managers; never hardcode.
- Log without leaking PII or secrets. Rotate logs.
- For web apps, enable HTTP security headers; CSRF tokens on state-changing ops.

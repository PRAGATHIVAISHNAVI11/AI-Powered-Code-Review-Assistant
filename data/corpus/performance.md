# Performance Tips
- Avoid N+1 DB queries; batch reads/writes.
- Prefer streaming large responses.
- Use lazy or incremental parsing when possible.
- Profile before optimizing; measure p95/p99.

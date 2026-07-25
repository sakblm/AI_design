# Security and company-use rules

- Prefer local assets and pinned dependencies.
- Treat relative paths as local only after recursively checking referenced CSS, JavaScript, fonts, images, imports, and runtime loaders.
- Flag `http:`, `https:`, protocol-relative URLs, remote `@import`, dynamic script creation, and package CDN loaders.
- Google Fonts may be used when company policy and the requester explicitly allow it. Treat it as an acknowledged network dependency, keep a system-font fallback, and record it in the QA report.
- Permission for Google Fonts does not imply permission for JavaScript CDNs, analytics, trackers, images, or arbitrary remote assets.
- Do not place credentials, cookies, access tokens, internal endpoints, personal data, or production records in wireframes or reports.
- Use synthetic examples for names, locations, IDs, prices, and messages unless the requester explicitly supplies approved test data.
- Do not upload internal screens or source to external services without explicit authorization.
- Record any required network access and its purpose in the QA report.
- A file opened from disk is not necessarily offline-safe; transitive runtime dependencies still count.

# Architecture overview
Data flows through read-only adapters, declarative mappings, validation, canonical contracts, persistence, services, APIs and the frontend. Facts may carry independent freshness and confidence. Source systems remain authoritative.

The JSON-backed API is only a local bootstrap. PostgreSQL repositories replace it after IDs, relationships, retention and precedence are confirmed. Future graph, tracing, optimization and notification capabilities should consume canonical events and retain human approval gates for operational/customer-facing actions.

# Naming conventions
- Python uses `snake_case`; React components and types use `PascalCase`.
- API paths are plural kebab-case; contract JSON fields use snake_case.
- Database tables are plural snake_case with opaque external-safe IDs.
- Adapters use `<source>_source.py`; mappings use `<source>_<version>.py`.
- Mock filenames contain `.mock.` and mock IDs start with `mock-`.

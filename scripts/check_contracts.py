import json
from pathlib import Path
json.loads(Path("packages/contracts/schemas/supply-chain-record.schema.json").read_text())
print("JSON contracts are syntactically valid")

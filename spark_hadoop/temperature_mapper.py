import sys
import json

for line in sys.stdin:
    data = json.loads(line)
    city = data.get("location", "Unknown")
    temperature = data.get("t_2m:C", 0)
    print(f"{city}\t{temperature}")

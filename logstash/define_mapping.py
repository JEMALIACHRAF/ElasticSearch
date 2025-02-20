import requests
import json

# ✅ Elasticsearch connection details
ES_HOST = "http://localhost:9200"
ES_INDEX = "weather_data"
AUTH = ("elastic", "rc5t-rQhGYoxyG3cP4Nb")  # Replace with your credentials

# ✅ Define the new mapping
mapping = {
    "mappings": {
        "properties": {
            "location": {
                "type": "text",  # Main text field for full-text search
                "fields": {
                    "keyword": {"type": "keyword"},  # For aggregations
                    "ngram": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer"
                    }
                }
            }
        }
    },
    "settings": {
        "analysis": {
            "analyzer": {
                "autocomplete_analyzer": {
                    "tokenizer": "autocomplete_tokenizer",
                    "filter": ["lowercase"]
                }
            },
            "tokenizer": {
                "autocomplete_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 10,
                    "token_chars": ["letter"]
                }
            }
        }
    }
}

# ✅ Apply the new mapping
response = requests.put(f"{ES_HOST}/{ES_INDEX}", auth=AUTH, headers={"Content-Type": "application/json"}, data=json.dumps(mapping))

if response.status_code == 200:
    print("✅ Mapping updated successfully!")
else:
    print(f"❌ Error updating mapping: {response.text}")


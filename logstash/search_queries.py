import requests
import json
import os
from datetime import datetime

# ✅ Configuration de l'accès à Elasticsearch
ES_HOST = "http://localhost:9200"
ES_INDEX = "weather_data"  # 🔍 Remplace par ton index réel
AUTH = ("elastic", "rc5t-rQhGYoxyG3cP4Nb")  # 🔑 Identifiants

# ✅ Dossier pour stocker les résultats
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ✅ Nom du fichier de stockage
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(LOG_DIR, f"results_{timestamp}.json")

# ✅ Dictionnaire pour stocker les résultats
query_results = {}

# ✅ Fonction pour exécuter une requête et enregistrer les résultats
def execute_query(query_body, description=""):
    """Exécute une requête Elasticsearch, affiche et enregistre les résultats"""
    url = f"{ES_HOST}/{ES_INDEX}/_search"
    response = requests.get(url, auth=AUTH, headers={"Content-Type": "application/json"}, data=json.dumps(query_body))
    
    if response.status_code == 200:
        results = response.json()
        query_results[description] = results  # 📌 Enregistre les résultats dans le dictionnaire
        
        print(f"\n🔍 {description}")
        print(json.dumps(results, indent=2))
    else:
        print(f"\n❌ Erreur ({response.status_code}) pour {description}: {response.text}")

# ✅ 1. Requête Textuelle : Recherche par lieu
text_query = {
    "query": {
        "match": {
            "location": "Paris"
        }
    }
}
execute_query(text_query, "🔍 Recherche Textuelle : Données de Paris")

# ✅ 2. Agrégation : Moyenne des températures par ville
agg_query = {
    "size": 0,
    "aggs": {
        "avg_temperature_per_city": {
            "terms": {"field": "location.keyword", "size": 10},
            "aggs": {
                "avg_temp": {"avg": {"field": "t_2m:C"}}
            }
        }
    }
}
execute_query(agg_query, "📊 Agrégation : Moyenne des températures par ville")

# ✅ 3. N-gram : Suggestion de ville avec 'Par'
ngram_query = {
    "query": {
    "match": {
      "location.ngram": "Par"
    }
  }

}
execute_query(ngram_query, "🔡 N-gram : Suggestion de ville avec 'Par'")

# ✅ 4. Fuzzy Matching : Recherche approximative pour 'Pariz'
fuzzy_query = {
  "query": {
    "match": {
      "location": {
        "query": "Pariz",
        "fuzziness": "AUTO"
      }
    }
  }
}

execute_query(fuzzy_query, "🤖 Fuzzy Matching : Recherche approximative pour 'Pariz'")

# ✅ 5. Série Temporelle : Température moyenne par jour
time_series_query = {
    "size": 0,
    "aggs": {
        "temperature_over_time": {
            "date_histogram": {
                "field": "timestamp",
                "calendar_interval": "day"
            },
            "aggs": {
                "avg_temperature": {"avg": {"field": "t_2m:C"}}
            }
        }
    }
}
execute_query(time_series_query, "📅 Série Temporelle : Évolution de la température")

# ✅ Sauvegarde des résultats dans un fichier JSON
with open(log_file, "w", encoding="utf-8") as f:
    json.dump(query_results, f, indent=4)

print(f"\n✅ Résultats enregistrés dans : {log_file}")

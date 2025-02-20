# **Rapport : Indexation et Visualisation de Données Massives**

## **1. Introduction**
Ce projet a pour objectif de construire un **pipeline de données** complet en utilisant **Kafka, Logstash, Elasticsearch, Kibana** et un traitement avancé via **Hadoop ou Spark**. Ce document présente la méthodologie suivie, les choix techniques effectués ainsi que les résultats obtenus.

---

## **2. Architecture du Pipeline**

### **Technologies utilisées**
- **Kafka** : Transmission des données collectées.
- **Logstash** : Transformation et indexation des données.
- **Elasticsearch** : Stockage et recherche des données.
- **Kibana** : Visualisation des données indexées.
- **Hadoop / Spark** : Traitement des données massives.

### **Schéma du Pipeline**

Voici un schéma du pipeline de données implémenté :

```
        [API] ---> [Kafka Producer] ---> [Kafka Topic] ---> [Kafka Consumer] ---> [Logstash] ---> [Elasticsearch] ---> [Kibana]
                                         |                                               |
                                         |                                               v
                                         |                                       [Hadoop / Spark]
                                         |
                                      [Stockage JSON]
```

1. **Collecte des données via une API météo**.
2. **Envoi des données à Kafka**.
3. **Transmission vers Logstash et indexation dans Elasticsearch**.
4. **Requêtes et visualisation des données dans Kibana**.
5. **Traitement avancé avec Hadoop ou Spark**.

---

## **3. Collecte des Données**

### **3.1 API utilisée**
Nous avons choisi une **API météo** qui fournit des données météorologiques en temps réel. Cette API fournit des paramètres tels que :

- **Ville** (exemple : Paris, Londres...)
- **Température actuelle (°C)**
- **Humidité (%)**
- **Pression atmosphérique (hPa)**
- **Vitesse du vent (m/s)**
- **Horodatage de la mesure**

### **3.2 Implémentation**
Le script `fetch_weather.py` extrait les données et les enregistre dans un fichier JSON (`weather_data.json`).

#### **Extrait du JSON :**
```json
{
  "city": "Paris",
  "temperature": 15.5,
  "humidity": 80,
  "pressure": 1012,
  "wind_speed": 5.2,
  "timestamp": "2025-02-19T18:45:00"
}
```

---

## **4. Transmission des Données avec Kafka**

### **4.1 Producteur Kafka**
Le fichier `producer.py` envoie les données collectées vers un **topic Kafka** en utilisant un producteur Kafka qui :
- Se connecte à l’API et récupère des données.
- Sérialise les données en format JSON.
- Envoie les données au topic Kafka.

### **4.2 Consommateur Kafka**
Le fichier `consumer.py` récupère les données du **topic Kafka** et les transmet à **Logstash**. Il :
- Lit les messages depuis le topic Kafka.
- Désérialise les données JSON.
- Vérifie l’intégrité des données.
- Envoie les données à Logstash pour traitement ultérieur.

#### **Exemple de message Kafka :**
```json
{
  "city": "Paris",
  "temperature": 15.5,
  "humidity": 80,
  "pressure": 1012,
  "wind_speed": 5.2,
  "timestamp": "2025-02-19T18:45:00"
}
```

---

## **5. Transformation et Indexation avec Logstash & Elasticsearch**

### **5.1 Configuration Logstash**
Le fichier `logstash.conf` définit le pipeline d’entrée et de sortie :
- Lecture des données depuis Kafka.
- Transformation des données (filtrage, formatage).
- Indexation dans Elasticsearch.

### **5.2 Mapping Elasticsearch**
Nous avons défini un **mapping personnalisé** (`define_mapping.py`) pour optimiser la recherche.

#### **Extrait du mapping JSON :**
```json
{
  "mappings": {
    "properties": {
      "city": { "type": "keyword" },
      "temperature": { "type": "float" },
      "humidity": { "type": "integer" },
      "pressure": { "type": "integer" },
      "wind_speed": { "type": "float" },
      "timestamp": { "type": "date" }
    }
  }
}
```

---

## **6. Requêtes Elasticsearch et Visualisation Kibana**
Les requêtes utilisées pour interroger Elasticsearch sont définies dans le fichier `logstash/search_queries.py`
Nous avons exécuté plusieurs requêtes :
1. **Requête textuelle** : Recherche des données par ville.
2. **Agrégation** : Calcul de la température moyenne par ville.
3. **Requête N-gram** : Recherche partielle.
4. **Requête fuzzy** : Recherche approximative.
5. **Requête temporelle** : Données météorologiques sur une période donnée.

1. **Requête textuelle** : Recherche de toutes les données pour une ville donnée.
   ```json
   {
     "query": {
       "match": { "city": "Paris" }
     }
   }
   ```

2. **Requête avec agrégation** : Moyenne de la température par ville.
   ```json
   {
     "size": 0,
     "aggs": {
       "avg_temp": { "avg": { "field": "temperature" } }
     }
   }
   ```

3. **Requête N-gram** : Recherche partielle sur le nom de la ville.
   ```json
   {
     "query": {
       "match": { "city.ngram": "Par" }
     }
   }
   ```

4. **Requête fuzzy** : Recherche approximative sur le nom de la ville.
   ```json
   {
     "query": {
       "fuzzy": { "city": { "value": "Pariz", "fuzziness": 2 } }
     }
   }
   ```

5. **Requête temporelle** : Recherche des données sur une période donnée.
   ```json
   {
     "query": {
       "range": {
         "timestamp": {
           "gte": "2025-02-19T00:00:00",
           "lte": "2025-02-20T00:00:00"
         }
       }
     }
   }
   ```

Les résultats sont stockés dans `logs/results_*.json`.

---

## **7. Traitement des Données avec Hadoop / Spark**

### **7.1 Hadoop (MapReduce)**
Nous avons utilisé `hadoop_processing.py` pour exécuter un traitement **MapReduce** sur les données météorologiques indexées.

#### **Processus Hadoop :**
1. **Mapper (`temperature_mapper.py`)** :
   - Extrait la température et la ville des enregistrements JSON.
   - Génère une clé-valeur sous la forme `(ville, température)`.
2. **Reducer (`temperature_reducer.py`)** :
   - Agrège les températures par ville.
   - Calcule la température moyenne pour chaque ville.

### **7.2 Spark (Traitement distribué)**
Le fichier `spark_processing.py` permet d’analyser les données avec **Spark** en exécutant :
- **Calcul de la moyenne de température par ville**.
- **Analyse des tendances de l’humidité sur une période donnée**.
- **Filtrage des températures extrêmes**.

### **7.3 Résultats du traitement**
Les résultats sont enregistrés dans `weather_analysis.csv`.


## **8. Conclusion**

Ce projet a permis de :
✅ Mettre en place un **pipeline de données** complet.
✅ Explorer des **requêtes avancées dans Elasticsearch**.
✅ Visualiser les données avec **Kibana**.
✅ Appliquer un **traitement big data avec Hadoop et Spark**.

---



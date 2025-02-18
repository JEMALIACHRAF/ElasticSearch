
# 📌 Processus Détaillé des Deux Approches avec Exemples Concrets d’Inputs/Outputs et Diagrammes de Séquences

## 🔷 Article 1 : Extraction et Interrogation de Graphes de Connaissances avec OKgraph

### 1. Diagramme de Séquence : Extraction et Interrogation de Graphes de Connaissances
```mermaid
sequenceDiagram
    participant Utilisateur
    participant OKgraph
    participant NLP_Tools
    participant WordEmbeddings
    participant RDF_Store

    Utilisateur->>+NLP_Tools: Texte brut (ex: "Rome est la capitale de l'Italie.")
    NLP_Tools->>+OKgraph: Tokenisation et nettoyage du texte (Output: ["Rome", "capitale", "Italie"])
    OKgraph->>+WordEmbeddings: Génération des vecteurs de mots (Word2Vec, FastText)
    WordEmbeddings->>+OKgraph: Modèle d’embeddings (Output: Représentation vectorielle des entités)
    OKgraph->>+OKgraph: Set Expansion (Output: Ajout d’entités similaires, ex: ["Rome", "Milan", "Venise"])
    OKgraph->>+OKgraph: Set Labeling (Output: Assignation de catégories, ex: "Ville")
    OKgraph->>+OKgraph: Relation Expansion (Output: Détection des relations entre entités, ex: "Rome -> capitale de -> Italie")
    OKgraph->>+OKgraph: Relation Labeling (Output: Nommage des relations détectées, ex: "capitale de")
    OKgraph->>+RDF_Store: Construction et stockage du Graphe de Connaissance (Output: Triples RDF stockés dans la base)
    Utilisateur->>+OKgraph: Requête en langage naturel (ex: "Quelle est la capitale de l'Italie ?")
    OKgraph->>+RDF_Store: Traduction en requête SPARQL et exécution
    RDF_Store->>Utilisateur: Résultats formatés (ex: "Rome")
```

**Exemple détaillé** :
- **Input** : Texte brut "Rome est la capitale de l'Italie. Milan est une ville italienne."
- **Étape 1** : Tokenisation → `['Rome', 'capitale', 'Italie', 'Milan', 'ville', 'italienne']`
- **Étape 2** : Word Embeddings génère des vecteurs de mots pour identifier les relations et entités similaires.
- **Étape 3** : Set Expansion trouve des entités proches (ex: "Venise", "Naples").
- **Étape 4** : Set Labeling classe les entités extraites en "Ville", "Pays", etc.
- **Étape 5** : Relation Expansion détecte les liens entre les entités (`Rome -> capitale de -> Italie`).
- **Étape 6** : Relation Labeling attribue un nom aux relations (`capitale de`, `situé en`).
- **Output final** : Un graphe RDF stocké avec les triples `{("Rome", "capitale de", "Italie"), ("Milan", "situé en", "Italie")}`.

---

## 🔷 Article 2 : Extraction Automatique d’Ontologies à partir de Documents

### 1. Diagramme de Séquence : Extraction d'Ontologies Automatiques
```mermaid
sequenceDiagram
    participant Utilisateur
    participant OntologyExtractor
    participant OWL_DB

    Utilisateur->>OntologyExtractor: Fournit un document texte/XML (ex: "Inception est un film de science-fiction.")
    OntologyExtractor->>OntologyExtractor: Tokenisation et calcul du TF-IDF (Output: ["Inception", "film", "science-fiction"])
    OntologyExtractor->>OntologyExtractor: Application de LSA et clustering hiérarchique (Output: Concepts "Film", "Science-fiction")
    OntologyExtractor->>OntologyExtractor: Extraction des concepts et relations sémantiques (Output: Ontologie hiérarchisée)
    OntologyExtractor->>OWL_DB: Stockage des concepts et relations dans une ontologie OWL (Output: Fichier OWL enregistré)
    Utilisateur->>OntologyExtractor: Pose une requête SPARQL (ex: "Quels sont les films de science-fiction ?")
    OntologyExtractor->>OWL_DB: Exécution de la requête SPARQL
    OWL_DB->>OntologyExtractor: Retour des résultats (Output: ["Inception"])
    OntologyExtractor->>Utilisateur: Génération d'une réponse structurée (ex: "Inception est un film de science-fiction.")
```
**Exemple détaillé** :
- **Input** : Document XML contenant "Inception est un film de science-fiction réalisé par Christopher Nolan."
- **Étape 1** : Tokenisation → `['Inception', 'film', 'science-fiction', 'Christopher', 'Nolan']`
- **Étape 2** : TF-IDF calcule les scores d’importance des mots-clés.
- **Étape 3** : LSA extrait des concepts clés `['Film', 'Science-fiction']`.
- **Étape 4** : Clustering hiérarchique regroupe les termes associés dans une structure taxonomique.
- **Output final** : Une ontologie OWL stockée avec `Film` comme concept principal et `Science-fiction` comme sous-classe.

### 2. Diagramme Explicatif : Fonctionnement du LSA avec Exemples
```mermaid
flowchart TD
    A[Documents texte] -->|Tokenisation & Stopwords| B[Matrice TF-IDF]
    B -->|Décomposition SVD| C[Matrices U, Σ, V]
    C -->|Réduction de dimension| D[Matrice U réduite]
    D -->|Extraction de concepts| E[Concepts extraits]
    E -->|Association aux documents| F[Scores pertinence]
```
**Exemple détaillé** :
- **Input** : "Les films de science-fiction sont captivants."
- **TF-IDF** : Matrice avec `['films', 'science-fiction', 'captivants']`.
- **SVD** : Décomposition en matrices U, Σ et V pour identifier les concepts dominants (`science-fiction` associé à `films`).
- **Output** : `Concept extrait = Science-fiction` avec `Score de pertinence = 0.89`.

### 3. Diagramme Explicatif : Fonctionnement de l'Agglomerative Clustering avec Exemples
```mermaid
flowchart TD
    A[Concepts extraits de LSA] -->|Calcul des distances entre concepts avec la similarité cosinus| B[Matrice de distance]
    B -->|Fusion itérative des concepts les plus proches selon la distance hiérarchique| C[Construction progressive de la hiérarchie]
    C -->|Définition des niveaux taxonomiques et classification des concepts| D[Ontologie structurée sous forme d'arbre]
    D -->|Exportation et stockage sous format OWL| E[Ontologie exploitable dans Protégé et autres éditeurs]
```
**Exemple détaillé** :
- **Input** : Concepts `['Film', 'Science-fiction', 'Thriller', 'Drame']`
- **Étape 1** : Matrice de distance cosinus entre les termes (ex : `Sim(Film, Science-fiction) = 0.85`).
- **Étape 2** : Fusion des concepts ayant les plus fortes similarités (`Film` et `Science-fiction` sont fusionnés).
- **Étape 3** : Classification hiérarchique des concepts (`Thriller` et `Drame` sont placés sous `Cinéma`).
- **Output final** : Ontologie structurée avec `Cinéma → [Science-fiction, Thriller, Drame]`.

---

💡 **Ce fichier README.md structure clairement les processus des deux articles avec des diagrammes enrichis et détaillés pour une meilleure compréhension et implémentation !** 🚀





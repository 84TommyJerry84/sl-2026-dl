# S3 et MongoDB

Ce projet met en place un petit pipeline de données avec Docker Compose, MinIO, DuckDB et MongoDB.

Le fichier `data/tram_stops.parquet` provient d'un précédent brief réalisé à partir de données GTFS. Il est réutilisé ici comme donnée d'entrée du pipeline.

## Architecture

Le projet utilise plusieurs services Docker :

```text
tram_stops.parquet
        |
        v
      Python
        |
        v
   MinIO - raw
        |
        v
     DuckDB
        |
        v
 MinIO - curated
        |
        v
      MongoDB
```

MinIO est utilisé comme stockage objet.

MongoDB est utilisé pour stocker des documents.

DuckDB est utilisé pour lire et agréger les fichiers Parquet.

Les services Docker communiquent entre eux avec leur nom de service, par exemple `minio:9000` et `mongo:27017`.

## Configuration

Copier le fichier d'exemple :

```powershell
Copy-Item config/.env.example config/.env
```

Puis compléter les variables dans `config/.env`.

Exemple de configuration :

```env
# MinIO
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=mot_de_passe
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET=test-data
MINIO_TEST_FILE=/app/data/tram_stops.parquet
MINIO_TEST_OBJECT=tram_stops.parquet
MINIO_RAW_BUCKET=raw
MINIO_CURATED_BUCKET=curated
MINIO_RAW_OBJECT=tram_stops.parquet
MINIO_CURATED_OBJECT=tram_stops_curated.parquet

# MongoDB
MONGO_ROOT_USER=mongo_admin
MONGO_ROOT_PASSWORD=mot_de_passe
MONGO_ENDPOINT=mongodb://mongo:27017
MONGO_DATABASE=transport
MONGO_COLLECTION=routes
MONGO_JSON_FILE=/app/data/routes.json
MONGO_CURATED_COLLECTION=tram_stop_counts
```

Le fichier `config/.env` est ignoré par Git.

## Lancer le projet

Pour construire les images et lancer tout le pipeline :

```powershell
docker compose --env-file config/.env up -d --build
```

Pour vérifier l'état des conteneurs :

```powershell
docker compose --env-file config/.env ps -a
```

MinIO et MongoDB doivent être `healthy`.

Les services `python`, `processor` et `loader` doivent terminer avec le code `Exited (0)`.

Pour afficher les logs :

```powershell
docker compose --env-file config/.env logs python processor loader
```

Les logs sont affichés dans le terminal et enregistrés dans le fichier `historique.log`.

Le temps d'exécution des différents points d'entrée est également mesuré.

## Partie 1 - MinIO et MongoDB

Le service `python` réalise les premiers tests du brief.

Avec MinIO, il :

- crée les buckets nécessaires ;
- envoie le fichier Parquet dans le bucket `test-data` ;
- relit le fichier depuis MinIO ;
- dépose ensuite le Parquet dans le bucket `raw`.

Avec MongoDB, il :

- charge les documents de `data/routes.json` ;
- recherche la ligne `T3a` ;
- réalise une agrégation pour compter le nombre d'arrêts par ligne.

Les arrêts sont directement imbriqués dans les documents représentant les lignes de transport.

## Partie 2 - Pipeline raw / curated

Le service `processor` télécharge le Parquet depuis le bucket `raw`.

DuckDB réalise ensuite une agrégation du nombre d'arrêts par ligne :

```text
line_name
stop_count
```

Le résultat est écrit dans un nouveau fichier Parquet puis envoyé dans le bucket `curated`.

Le service `loader` télécharge ensuite ce fichier et charge les résultats dans la collection MongoDB `tram_stop_counts`.

L'ordre d'exécution est contrôlé avec les `healthcheck` et `depends_on` de Docker Compose.

## Vérification du code

Le code peut être vérifié avec Ruff :

```powershell
ruff format src
ruff check src
```

La commande `ruff check src` doit afficher :

```text
All checks passed!
```

## Arrêter le projet

Pour arrêter les conteneurs :

```powershell
docker compose --env-file config/.env down
```

Pour supprimer également le volume MinIO et repartir de zéro :

```powershell
docker compose --env-file config/.env down -v
```

## Questions ouvertes

### Pourquoi faire transiter la donnée par le stockage objet plutôt que d'aller directement de GTFS à MongoDB ?

Le stockage objet permet de conserver les fichiers bruts avant leur transformation.

Si le traitement change ou produit une erreur, il est possible de repartir du fichier présent dans la zone `raw` sans devoir récupérer de nouveau les données d'origine.

Il permet aussi de séparer le stockage des fichiers et leur chargement dans MongoDB.

### À quoi servent les zones raw et curated ? Pourquoi ne pas avoir une seule zone ?

La zone `raw` contient les données brutes, avant traitement.

La zone `curated` contient les données nettoyées ou transformées, prêtes à être utilisées.

Séparer les deux permet de conserver les données d'origine tout en ayant une version préparée pour les usages suivants.
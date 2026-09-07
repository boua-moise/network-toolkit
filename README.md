# Network Toolkit

Network Toolkit est un scanner TCP séquentiel développé en Python
dans un objectif pédagogique. Il permet de tester une plage de ports
sur une cible autorisée et d'afficher les ports qui acceptent une
connexion TCP.

## Fonctionnalités

- Scan séquentiel d'une plage de ports TCP
- Résolution d'une adresse IPv4 ou d'un nom d'hôte
- Plage configurable avec `--ports`
- Timeout configurable avec `--timeout`
- Timeout configurable avec `--threads`
- Validation des arguments
- Validation des ports de 1 à 65535
- Gestion des erreurs réseau
- Arrêt propre avec `Ctrl+C`
- Affichage de la progression
- Affichage des ports ouverts

## Architecture

```text
network-toolkit/
├── scanner.py
├── README.md
└── .gitignore
```

## Prérequis

- Python 3.10 ou version ultérieure
- Git, uniquement pour cloner ou contribuer au projet

Le projet utilise uniquement la bibliothèque standard Python.
Aucune dépendance externe n'est nécessaire.

## Installation

Clonez le dépôt :

```bash
git clone URL_DU_DEPOT
```

Entrez dans le répertoire :

```bash
cd network-toolkit
```

Vérifiez la version de Python :

```bash
python --version
```

## Utilisation

Syntaxe générale :

```bash
python scanner.py CIBLE --ports DEBUT-FIN --timeout SECONDES --threads ENTIER
```

- `CIBLE` : adresse IPv4 ou nom d'hôte.
- `--ports` : plage TCP inclusive au format `DEBUT-FIN`.
- `--timeout` : délai maximal par tentative, en secondes.
- `--threads` : Nombre de workers utilisés pour traiter la file de ports.

### Scanner les ports 20 à 100

```bash
python scanner.py 127.0.0.1 --ports 20-100
```

### Modifier le timeout

```bash
python scanner.py 127.0.0.1 --ports 20-100 --timeout 0.5
```

### Tester un seul port

```bash
python scanner.py 127.0.0.1 --ports 8000-8000
```

### Scan Multithreads

```bash
python scanner.py 127.0.0.1 --ports 1-1000 --threads 50
```

### Afficher l'aide

```bash
python scanner.py --help
```

## Exemple contrôlé

Dans un premier terminal, démarrez un serveur HTTP local :

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Dans un second terminal, lancez le scanner :

```bash
python scanner.py 127.0.0.1 --ports 7995-8005
```

Le port `8000` devrait être affiché comme ouvert.

Arrêtez ensuite le serveur avec `Ctrl+C`, puis relancez le scanner.
Le port `8000` ne devrait plus apparaître.

## Fonctionnement général

Pour chaque port de la plage, le programme :

1. crée un nouveau socket TCP IPv4 ;
2. configure le timeout demandé ;
3. tente d'établir une connexion ;
4. enregistre le port si la connexion réussit ;
5. ferme automatiquement le socket ;
6. passe au port suivant.

## Limites

- Le programme teste uniquement les connexions TCP.
- UDP et IPv6 ne sont pas pris en charge dans cette version.
- Une connexion réussie ne garantit pas l'identité du service.
- Un timeout ne prouve pas qu'un port est fermé.
- Un timeout trop court peut produire des faux négatifs.

## Utilisation responsable

Ce projet est destiné à l'apprentissage de Python et des concepts
réseau.

Utilisez-le uniquement :

- sur vos propres machines ;
- dans un laboratoire personnel ;
- sur des systèmes pour lesquels vous disposez d'une autorisation
  explicite.

L'utilisateur est responsable du respect des règles et lois
applicables à son environnement.

## Tests manuels

### Serveur local actif

```bash
python -m http.server 8000 --bind 127.0.0.1
python scanner.py 127.0.0.1 --ports 7995-8005
```

Résultat attendu : le port `8000` est détecté.

### Serveur local arrêté

```bash
python scanner.py 127.0.0.1 --ports 7995-8005
```

Résultat attendu : le port `8000` n'est pas détecté.

### Plage inversée

```bash
python scanner.py 127.0.0.1 --ports 100-20
```

Résultat attendu : la plage est refusée.

### Port hors limites

```bash
python scanner.py 127.0.0.1 --ports 65000-70000
```

### Threads supérieurs au nombre de ports

```bash
python scanner.py 127.0.0.1 --ports 8000-8000 --threads 50
```

Résultat attendu : la plage est refusée.

## Améliorations possibles

- Ajouter des tests automatisés
- Ajouter un mode silencieux
- Exporter les résultats en JSON
- Ajouter un résumé de la durée du scan
- Étudier IPv6
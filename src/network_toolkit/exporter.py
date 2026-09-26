import json
from dataclasses import asdict
from network_toolkit.scanner import ResultScan


def creation_rapport(data:ResultScan):
    return asdict(data)


def ecriture_rapport(chemin: str, rapport: dict):
    try:
        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(rapport, fichier, indent=2, ensure_ascii=False)
            
    except PermissionError as e:
        raise PermissionError("Interdit d'écrire")

    except FileNotFoundError as e:
        raise FileNotFoundError("Impossible de créer le fichier")
from pathlib import Path

output = Path("results") / "result.json"
print(output)
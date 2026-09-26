import argparse, sys
from pathlib import Path
from network_toolkit import validation, exporter, scanner


def analyser_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scanner TCP séquentiel.")
    parser.add_argument(
        "cible",
        help="Cible à tester",
        type=validation.resoudre_cible
    )
    parser.add_argument(
        "--ports",
        help="Plage de port à scanner, exemple 20-50",
        type=validation.analyser_plage_ports,
        default=(80,80)
    )
    parser.add_argument(
        "--timeout",
        help="Délai maximal par port en secondes, par défaut : 0.5.",
        type=validation.analyser_timeout,
        default=0.5
    )
    parser.add_argument(
        "--threads",
        default=1,
        type=validation.validation_threads,
        help="Nombre maximal de thread, par défaut: 1"
    )
    parser.add_argument(
        "--output",
        default=None,
        type=str,
        help="Fichier d'exportation des résultats, Defaut: None"
    )
    return parser.parse_args()


def afficher_resultats(rapport: dict) -> None:

    """
    Affiche le résultat du scan
    Returns:
        None
    """

    print("#" * 40, "RESULTAT", "#" * 40)

    print(f"""
Network Toolkit v0.2

Cible : {rapport["hote"]}
Adresse résolue: {rapport["hote_relosolu"]}
Ports : {rapport["plage_port"]["debut"]}-{rapport["plage_port"]["fin"]}
Workers : {rapport["threads_reel"]}
Timeout : {rapport["timeout"]} s

Ports ouverts
--------------""")
    
    for port_ouvert in rapport["ports_ouvert"]:
        print(port_ouvert)

    if not rapport["ports_ouvert"]:
        print("Aucun port ouvert")

    print(f"""
Résumé
------
Ports analysés : {rapport["nbr_ports_analyser"]}
Ports ouverts : {rapport["nbr_ports_ouvert"]}
Durée : {round(rapport["duree"], ndigits=1)} s""")


def main():

    arguments = analyser_arguments()

    dossier = Path("results")
    dossier.mkdir(exist_ok=True)

    nom_fichier = arguments.output

    config = scanner.ConfigScan(
        arguments.cible[0],
        arguments.cible[1],
        arguments.ports[0],
        arguments.ports[1],
        arguments.timeout,
        arguments.threads,
        arguments.output
    )

    try:
        resultat = scanner.run_scan(config)
        rapport = exporter.creation_rapport(resultat)
        afficher_resultats(rapport)

        if nom_fichier:
            chemin = dossier / nom_fichier
            exporter.ecriture_rapport(chemin, rapport)
            print(f"Export : succès")  
        
        else:
            print("Export : non demandé")

        return 0

    except ValueError:
        print(
            "Erreur : la cible indiquée est invalide.",
            file=sys.stderr,
        )
        # exporter.ecriture_rapport("erreur/exception.json", erreur_scann)
        return 2

    except FileNotFoundError:
        print("Export: échoué")
        print(
            f"Erreur : impossible d'écrire le fichier JSON demandé.",
            file=sys.stderr,
        )
        # exporter.ecriture_rapport("erreur/exception.json", erreur_scann)
        return 2

    except KeyboardInterrupt:
        print(
            "Scan interrompu par l'utilisateur.",
            file=sys.stderr,
        )
        # exporter.ecriture_rapport("erreur/exception.json", erreur_scann)
        return 130

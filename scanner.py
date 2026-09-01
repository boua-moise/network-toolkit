"""Outil pédagogique de vérification d'un port TCP."""

import socket, argparse, errno, sys


########################### Scanne des ports #########################################

def scanner_port(hote: str, port: int, timeout: float = 0.5) -> tuple[int, str]:

    """
    Vérifie si une connexion TCP peut être établie.

    Args:
        adresse_ip: Adresse IPv4 de la machine cible
        port: Port du service à atteindre
        timeout: Durée maximale d'attente en secondes

    Returns:
        True si la connexion réussit, False si non
    """

    etat = ""

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_scan:
        
                socket_scan.settimeout(timeout)
        
                resultat_test = socket_scan.connect_ex((hote, port))

    except OSError:

        return False

    if resultat_test == 0:
        etat = "OUVERT"
    elif resultat_test == errno.ECONNREFUSED:
        etat = "FERME"
    elif resultat_test == errno.ETIMEDOUT:
        etat = "TIMEOUT"
    else:
        etat = "INACCESSIBLE"

    return (port, etat)


def scanner_plage_ports(
        hote: str, 
        premier_port: int, 
        dernier_port: int, 
        timeout: float = 0.5
    ) -> list[tuple[int, str]]:

    """
    Vérifie si plusieur connexion peuvent être établies en se basant sur une plage

    Args:
        adresse_ip: Adresse IP de la machine cible
        premier_port: Entier désignant le début de la plage de port
        dernier_port: Entier désignant la fin de la plage de port
        timeout: Durée maximale d'attente en seconde
    Returns:
        [(port1, etat), (port2, etat), (port3, etat)...] contenant les ports ouverts, [] si aucun port ouvert
    """

    ports_ouverts: list[tuple[int, str]] = []
    total_ports = dernier_port - premier_port + 1

    for compte, port in enumerate(range(premier_port, dernier_port + 1), start=1):

        ports_ouverts.append(scanner_port(hote, port, timeout))

        print(f"[{compte}/{total_ports}] Test du port {port}")

    return ports_ouverts

def analyser_timeout(texte:str) -> float:
    try:
        timeout = float(texte)

    except ValueError as erreur:
        raise argparse.ArgumentTypeError(
            "La valeur saisir est fausse"
        ) from erreur

    if timeout < 0:
        raise argparse.ArgumentTypeError(
            "le timeout doit être strictement supérieur à zéro"
        )

    return timeout


########################### Sortie du scanne des ports #########################################

def afficher_resultats(hote:str, ports_ouverts:tuple[int, str]) -> None:

    """
    Affiche le résultat du scan
    Returns:
        None
    """

    print("#" * 40, "RESULTAT", "#" * 40)

    print(f"Résultat des tests de ports ouverts sur {hote}")

    if not ports_ouverts:

        print("Aucun port ouvert")

    else:

        for port, etat in ports_ouverts:
            if etat == "OUVERT":
                print(f"- Port {port} {etat}")


########################### Vériffication d'adresse IP #########################################

def resoudre_cible(cible: str) -> str:

    """ 
    Résout une cible en une adresse IPv4. 
      
    Raises: 
        ValueError: Si la cible ne peut pas être résolue. 
    """ 

    try:
        cible = socket.gethostbyname(cible)
        return cible

    except socket.gaierror as erreur:
        raise ValueError(
            "La cible fournit est invalide"
        ) from erreur


########################### Vériffication de plage #########################################

def analyser_plage_ports(texte: str) -> tuple[int, int]:
    """
    Convertit une chaîne DEBUT-FIN en un tuple de ports valides.

    Args: 
        texte: Plage reçue depuis le terminal.
    
    Returns: 
        Un tuple contenant le premier et le dernier port.

    Raises: 
        argparse.ArgumentTypeError: Si le format ou les ports sont invalides.
    
    """

    parties = texte.split("-")

    if len(parties) != 2:
        raise argparse.ArgumentTypeError(
            "la plage doit respecter le format DEBUT-FIN"
        )

    debut_texte, fin_texte = parties 

    try:
        port_debut = int(debut_texte)
        port_fin = int(fin_texte)

    except ValueError as erreur:
        raise argparse.ArgumentTypeError(
            "les deux ports doivent être des nombres entiers"
        ) from erreur

    if not ((1 <= port_debut <= 65535) and (1 <= port_fin <= 65535)):
        raise argparse.ArgumentTypeError(
            "les ports doivent être compris entre 1 et 65535"
        )

    if port_debut > port_fin:
        raise argparse.ArgumentTypeError(
            "le premier port doit être inférieur ou égal au dernier"
        )

    return port_debut, port_fin


########################### Scanne des ports #########################################

def analyser_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scanner TCP séquentiel.")
    parser.add_argument(
        "cible",
        help="Cible à tester",
        type=resoudre_cible
    )
    parser.add_argument(
        "--ports",
        help="Plage de port à scanner, exemple 20-50",
        type=analyser_plage_ports,
        default=(80,80)
    )
    parser.add_argument(
        "--timeout",
        help="Délai maximal par port en secondes, par défaut : 0.5.",
        type=analyser_timeout,
        default=0.5
    )
    return parser.parse_args()


########################### Fonction principale #########################################

def main():

    try:
        arguments = analyser_arguments()
        print("\nVeuillez patienter, scan en cours...\n")
        ports_ouverts = scanner_plage_ports(arguments.cible, arguments.ports[0], arguments.ports[1])
        afficher_resultats(arguments.cible, ports_ouverts)
        return 0

    except ValueError:
        print(
            "Erreur : la cible indiquée est invalide.",
            file=sys.stderr,
        )
        return 2

    except KeyboardInterrupt:
        print(
            "Scan interrompu par l'utilisateur.",
            file=sys.stderr,
        )
        return 130

if __name__ == "__main__":
    sys.exit(main())

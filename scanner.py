"""Outil pédagogique de vérification d'un port TCP."""

import socket, argparse, errno, sys, threading, queue, time, json


########################### Scanne des ports #########################################

def scanner_port(hote: str, port: int, erreur_scan: dict, timeout: float = 0.5) -> bool:

    """
    Vérifie si une connexion TCP peut être établie.

    Args:
        adresse_ip: Adresse IPv4 de la machine cible
        port: Port du service à atteindre
        timeout: Durée maximale d'attente en secondes

    Returns:
        True si la connexion réussit, False si non
    """

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_scan:
        
                socket_scan.settimeout(timeout)
        
                resultat_test = socket_scan.connect_ex((hote, port))

    except OSError as erreur:

        erreur_scan[f"{port}"] = f"Erreur: {erreur}"

        return False

    if resultat_test == 0:
        etat = "OUVERT"
        return resultat_test == 0
    elif resultat_test == errno.ECONNREFUSED:
        etat = "FERME"
    elif resultat_test == errno.ETIMEDOUT:
        etat = "TIMEOUT"
    else:
        etat = "INACCESSIBLE"


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

        ports_ouverts.append(scanner_port(hote, port, {}, timeout))

        print(f"[{compte}/{total_ports}] Test du port {port}")

    return ports_ouverts


def analyser_timeout(texte: str) -> float:
    try:
        timeout = float(texte)

    except ValueError as erreur:
        raise argparse.ArgumentTypeError(
            "La valeur saisir est fausse"
        ) from erreur

    if not timeout > 0:
        raise argparse.ArgumentTypeError(
            "le timeout doit être strictement supérieur à zéro"
        )

    return timeout


########################### Sortie du scanne des ports #########################################

def afficher_resultats(rapport: dict, chemin: str) -> None:

    """
    Affiche le résultat du scan
    Returns:
        None
    """

    print("#" * 40, "RESULTAT", "#" * 40)

    print(f"""
Network Toolkit v0.2

Cible : {rapport["target"]}
Adresse résolue: {rapport["resolved_ip"]}
Ports : {rapport["port_range"]["start"]}-{rapport["port_range"]["end"]}
Workers : {rapport["threads_réel"]}
Timeout : {rapport["timeout"]} s

Ports ouverts
--------------""")
    
    for port_ouvert in rapport["open_ports"]:
        print(port_ouvert)

    if not rapport["open_ports"]:
        print("Aucun port ouvert")

    print(f"""
Résumé
------
Ports analysés : {rapport["analyse_ports"]}
Ports ouverts : {rapport["open_port_count"]}
Durée : {round(rapport["duration_seconds"], ndigits=1)} s""")

    if chemin:
        chemin = "results/" + chemin
        creation_rapport(chemin, rapport)
        print(f"Export : {chemin}")
            

    else:
        print("Export : non demandé")


def creation_rapport(chemin: str, rapport: dict):
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(rapport, fichier, indent=2, ensure_ascii=False)


########################### Vériffication d'adresse IP #########################################

def resoudre_cible(hote: str) -> str:

    """ 
    Résout une cible en une adresse IPv4. 
      
    Raises: 
        ValueError: Si la cible ne peut pas être résolue. 
    """ 

    try:
        cible = socket.gethostbyname(hote)
        return hote, cible

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


def validation_threads(thread: str) -> int:
    WORKER_MIN = 1
    WORKER_MAX = 200
    result = 0
    
    try:
        result = int(thread)

    except ValueError:
        raise argparse.ArgumentTypeError("Veuillez saisir une valeur entière")

    if result <= 0:
        raise argparse.ArgumentTypeError("Veuillez saisir une valeur surpérieur à 0")

    if not (WORKER_MIN <= result <= WORKER_MAX):
        raise argparse.ArgumentTypeError("La valeur saisir doit être comprise entre 1 et 200")

    return result


########################### Vérification des arguments #########################################

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
    parser.add_argument(
        "--threads",
        default=1,
        type=validation_threads,
        help="Nombre maximal de thread, par défaut: 1"
    )
    parser.add_argument(
        "--output",
        default=None,
        type=str,
        help="Fichier d'exportation des résultats, Defaut: None"
    )
    return parser.parse_args()


########################### Threading #########################################

def worker(hote:str, timeout: float, file_ports, ports_ouvert: list[int], erreur_scan: dict, verrou:threading.Lock) -> None:

    while True:

        try:
            port = file_ports.get()

            if port is None:
                return 

            if scanner_port(hote, port, erreur_scan, timeout):
                with verrou:
                    ports_ouvert.append(port)

        except OSError as erreur:
            erreur_scan[f"{port}"] = f"Erreur: {erreur}"

        finally:
            file_ports.task_done()


def nombre_worker_requis(threads: int, nbr_ports: int):
    worker_reel = threads

    if threads > nbr_ports:
        worker_reel = nbr_ports

    return worker_reel


########################### Fonction principale #########################################

def main():

    arguments = analyser_arguments()

    port_debut, port_fin = arguments.ports

    nombre_ports = len(range(port_debut, port_fin+1))

    NOMBRE_WORKER_SENTINELLE = nombre_worker_requis(arguments.threads, nombre_ports)

    threads: list[threading.Thread] = []
    ports_ouverts: list[int] = []
    erreur_scann = {}

    rapport = {
        "target": arguments.cible[0],
        "resolved_ip": arguments.cible[1],
        "port_range": {
            "start": port_debut,
            "end": port_fin
        },
        "threads": arguments.threads,
        "threads_réel": NOMBRE_WORKER_SENTINELLE,
        "timeout": arguments.timeout,
        "duration_seconds": 0,
        "open_ports": [],
        "analyse_ports": port_fin - port_debut + 1,
        "open_port_count": 0,
    }

    file_ports = queue.Queue(maxsize=60000)
    verrou = threading.Lock()

    debut = time.perf_counter()

    try:
        for port in range(arguments.ports[0], arguments.ports[1]+1):
            file_ports.put(port)

        for _ in range(NOMBRE_WORKER_SENTINELLE):
            file_ports.put(None)

        for _ in range(NOMBRE_WORKER_SENTINELLE):
            thread = threading.Thread(
                target=worker,
                args=(arguments.cible[1], arguments.timeout, file_ports, ports_ouverts, erreur_scann, verrou)
            )
            thread.start()
            threads.append(thread)

        file_ports.join()

        for thread in threads:
            thread.join()

        fin = time.perf_counter()
        duree = fin - debut
        ports_ouverts.sort()

        rapport["duration_seconds"] = duree
        rapport["open_ports"] = ports_ouverts
        rapport["open_port_count"] = len(ports_ouverts)

        afficher_resultats(rapport, arguments.output)
        
        return 0

    except ValueError:
        print(
            "Erreur : la cible indiquée est invalide.",
            file=sys.stderr,
        )
        creation_rapport("erreur/exception.json", erreur_scann)
        return 2

    except FileNotFoundError:
        print("Export: échoué")
        print(
            f"Erreur : impossible d'écrire le fichier JSON demandé. Chemin '{arguments.output}' incorrect",
            file=sys.stderr,
        )
        creation_rapport("erreur/exception.json", erreur_scann)
        return 2

    except KeyboardInterrupt:
        print(
            "Scan interrompu par l'utilisateur.",
            file=sys.stderr,
        )
        creation_rapport("erreur/exception.json", erreur_scann)
        return 130

if __name__ == "__main__":
    sys.exit(main())

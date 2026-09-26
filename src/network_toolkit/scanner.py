from dataclasses import dataclass
import queue, threading, time, socket

@dataclass
class ConfigScan:
    hote: str
    hote_relosolu: str
    port_debut: int
    port_fin: int
    timeout: float = 0.5
    threads: int = 1
    output: str | None = None

@dataclass
class ResultScan:
    hote: str
    hote_relosolu: str
    plage_port: dict[str, int]
    threads: int
    threads_reel: int
    timeout: float
    duree: float
    ports_ouvert: list[int]
    nbr_ports_analyser: int
    nbr_ports_ouvert: int



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
    
    return resultat_test == 0


def worker(hote: str, timeout: float, file_ports, ports_ouvert: list[int], erreur_scan: dict, verrou:threading.Lock) -> None:
    count = 1
    while True:

        try:
            port = file_ports.get()

            if port is None:
                return 

            if scanner_port(hote, port, erreur_scan, timeout):
                with verrou:
                    ports_ouvert.append(port)

        except OSError as erreur:
            erreur_scan[f"{count+1}"] = f"Erreur: {erreur}"

        finally:
            file_ports.task_done()


def nombre_worker_requis(threads: int, nbr_ports: int):
    worker_reel = threads

    if threads > nbr_ports:
        worker_reel = nbr_ports

    return worker_reel


def run_scan(conf: ConfigScan) -> ResultScan:

    file_ports = queue.Queue(maxsize=65735)
    verrou = threading.Lock()
    ports_ouverts: list[int] = []
    erreur_scann = {}
    threads: list[threading.Thread] = []
    nbr_ports = conf.port_fin - conf.port_debut + 1
    threads_sentinelle = nombre_worker_requis(conf.threads, nbr_ports)

    for port in range(conf.port_debut, conf.port_fin + 1):
        file_ports.put(port)

    for _ in range(threads_sentinelle):
        file_ports.put(None)

    debut = time.perf_counter()

    for _ in range(threads_sentinelle):
        thread = threading.Thread(target=worker, 
        args=(conf.hote, conf.timeout, file_ports, ports_ouverts, erreur_scann, verrou))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    file_ports.join()

    fin = time.perf_counter()

    duree = fin - debut

    return ResultScan(
        conf.hote,
        conf.hote_relosolu,
        {"debut": conf.port_debut, "fin": conf.port_fin},
        conf.threads,
        threads_sentinelle,
        conf.timeout,
        duree,
        ports_ouverts,
        nbr_ports,
        len(ports_ouverts)
    )
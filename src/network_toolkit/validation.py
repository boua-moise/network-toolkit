import socket, argparse

def resoudre_cible(hote: str) -> tuple[str, str]:

    """ 
    Résout une cible en une adresse IPv4. 

    Args:
        hote: une adresse ip ou un nom de domaine

    Return:
        renvoit un tuple contenant la hote et la resolution IP
      
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


def analyser_timeout(timeout_saisi: str) -> float:

    """
    Analyse la valeur reçue comme timeout en second

    Args:
        timeout_saisi: str

    Return:
        un nombre flotant

    Raises:
        ValueError: si la valeur entrer ne correspond pas au type attendu
        ArgumentTypeError: si la valeur est négative ou nul
    """

    try:
        timeout = float(timeout_saisi)

    except ValueError as erreur:
        raise argparse.ArgumentTypeError(
            "La valeur saisir est fausse"
        ) from erreur

    if not timeout > 0:
        raise argparse.ArgumentTypeError(
            "le timeout doit être strictement supérieur à zéro"
        )

    return timeout


def analyser_plage_ports(texte: str) -> tuple[int, int]:

    """
    Convertit une chaîne DEBUT-FIN en un tuple de ports valides

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

    """
    Vérifie que le Thead est du bon type et compris entre les limites

    Args:
        thread: str

    Return:
        Renvoie un entier

    Raises:
        ValueError: si le type demander ne correspond pas à un eniter
        argparse.AgumentTypeError: si la valeur n'est pas dans le bon intervall ou est nul
    """

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
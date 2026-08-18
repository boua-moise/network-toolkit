"""Outil pédagogique de vérification d'un port TCP."""

import socket


def check_port(target_ip, target_port, timeout=2):
    """
    Vérifie si une connexion TCP peut être établie.

    Args:
        target_ip: Adresse IPv4 de la machine cible.
        target_port: Port TCP à vérifier.
        timeout: Durée maximale d'attente en secondes. par défaut 2

    Returns:
        True si la connexion réussit, sinon False.
    """

    try:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as client_socket:
            client_socket.settimeout(timeout)
            client_socket.connect((target_ip, target_port))

        return True

    except ConnectionRefusedError:
        return False

    except TimeoutError:
        print("La tentative de connexion a dépassé le délai autorisé.")
        return False

    except OSError as error:
        print(f"Une erreur réseau s'est produite : {error}")
        return False


def main():
    """Lance le test d'un port TCP."""

    target_ip = "127.0.0.1"
    target_port = 8000

    print(f"Test de {target_ip}:{target_port}...")

    is_open = check_port(target_ip, target_port)

    if is_open:
        print(f"Le port {target_port} est ouvert.")
    else:
        print(f"Le port {target_port} n'est pas accessible.")


if __name__ == "__main__":
    main()
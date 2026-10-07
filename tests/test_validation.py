import pytest, argparse
from network_toolkit import validation


########## Préparation d'une fixture ########################

@pytest.fixture
def rapport_scan():
    return {
        "hote": "127.0.0.1",
        "hote_relosolu": "127.0.0.1",
        "plage_port": {
            "debut": 7995,
            "fin": 8005
        },
        "threads": 5,
        "threads_reel": 5,
        "timeout": 0.5,
        "duree": 0.0026317499996366678,
        "ports_ouvert": [
            8000
        ],
        "nbr_ports_analyser": 11,
        "nbr_ports_ouvert": 1
    }


################## Tests des plages valides #############################

@pytest.mark.parametrize(
        "plage_brut, port_debut_fin",
        [
            ("1-200", (1, 200)),
            ("1024-65535", (1024, 65535)),
            ("100-2030", (100, 2030)),
            ("80-80", (80, 80))
        ]
)
def test_analyse_plage_port_valides(plage_brut, port_debut_fin):

    plage = validation.analyser_plage_ports(plage_brut)

    assert plage == port_debut_fin


################## Tests des plages invalides #############################

@pytest.mark.parametrize(
        "plage, erreur",
        [
            ("100-20", argparse.ArgumentTypeError),
            ("0-100", argparse.ArgumentTypeError),
            ("1-65536", argparse.ArgumentTypeError),
            ("a-b", argparse.ArgumentTypeError),
            ("45", argparse.ArgumentTypeError),
            ("", argparse.ArgumentTypeError),
            ("12-50,", argparse.ArgumentTypeError)
        ]
)
def test_analyse_plage_port_plage_invalides(plage, erreur):
    with pytest.raises(erreur):
        validation.analyser_plage_ports(plage)



################## Tests des threads valides #########################

@pytest.mark.parametrize(
    "thread, resultat",
    [
        ("1", 1),
        ("10", 10),
        ("200", 200)
    ]
)
def test_validation_thread_valides(thread, resultat):
    assert validation.validation_threads(thread) == resultat


################ Tests des threads invalides #########################

@pytest.mark.parametrize(
    "thread, erreur",
    [
        ("-1", argparse.ArgumentTypeError),
        ("0", argparse.ArgumentTypeError),
        ("201", argparse.ArgumentTypeError),
        ("", argparse.ArgumentTypeError)
    ]
)
def test_validation_thread_invalides(thread, erreur):
    with pytest.raises(erreur):
        validation.validation_threads(thread)


################ Tests des timeouts valides #########################

@pytest.mark.parametrize(
    "timeout, resultat",
    [
        ("0.1", 0.1),
        ("0.5", 0.5),
        ("1", 1)
    ]
)
def test_validation_timeout_valides(timeout, resultat):
    assert validation.analyser_timeout(timeout) == resultat


################# Tests des timeouts invalides #############################

@pytest.mark.parametrize(
    "timeout, erreur",
    [
        ("-1", argparse.ArgumentTypeError),
        ("0", argparse.ArgumentTypeError),
        ("-0.1", argparse.ArgumentTypeError),
        ("", argparse.ArgumentTypeError)
    ]
)
def test_validation_timeout_invalides(timeout, erreur):
    with pytest.raises(erreur):
        validation.analyser_timeout(timeout)

#À réaliser avec un mock au Jour 4 pour la résolution de la cible
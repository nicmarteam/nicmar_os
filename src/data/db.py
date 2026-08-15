"""
Conexiune PostgreSQL pentru NicMar OS.

Sursă: MISSION-VERTICAL-SLICE-CONTRACT v1, secțiunea 1.5.
Regulă: acest fișier conține strict conexiunea la bază de date.
Nicio logică de business (nicio interogare specifică unui motor) nu
aparține aici — motoarele (`MissionEngine`, `RuleEngine`) își scriu
propriile interogări, folosind conexiunea furnizată de acest modul.
"""

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg import Connection


def get_database_url() -> str:
    """
    Citește URL-ul de conexiune din variabila de mediu DATABASE_URL.

    Nu se hardcodează nicio valoare implicită de producție — dacă
    variabila lipsește, eșuăm explicit, nu presupunem o valoare.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL nu este setat. "
            "Exemplu: postgresql://user:parola@localhost:5432/nicmar_os"
        )
    return url


@contextmanager
def get_connection() -> Iterator[Connection]:
    """
    Furnizează o conexiune PostgreSQL, ca context manager.

    Uz:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

    Conexiunea face commit automat la ieșirea fără eroare din blocul
    `with` și rollback automat dacă apare o excepție — comportament
    implicit al psycopg3, nu logică adăugată aici.
    """
    conn = psycopg.connect(get_database_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

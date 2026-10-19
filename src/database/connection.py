import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

# Cargar las variables de entorno
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def proteger_valor(valor: str) -> str:
    """Escapa caracteres especiales para ODBC."""
    return "{" + valor.replace("}", "}}") + "}"


def get_connection():
    """Crear una conexión con AdventureWorks2022."""

    variables = [
        "DB_SERVER",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD"
    ]

    faltantes = [
        variable for variable in variables
        if not os.getenv(variable)
    ]

    if faltantes:
        raise ValueError(
            "Faltan variables de entorno: "
            + ", ".join(faltantes)
        )

    partes = [
        "DRIVER={ODBC Driver 17 for SQL Server}",
        f"SERVER={proteger_valor(os.environ['DB_SERVER'])}",
        f"DATABASE={proteger_valor(os.environ['DB_NAME'])}",
        f"UID={proteger_valor(os.environ['DB_USER'])}",
        f"PWD={proteger_valor(os.environ['DB_PASSWORD'])}",
        "Encrypt=yes",
        "TrustServerCertificate="
        + os.getenv("DB_TRUST_SERVER_CERTIFICATE", "no"),
    ]

    connection_string = ";".join(partes) + ";"

    return pyodbc.connect(
        connection_string,
        timeout=10
    )
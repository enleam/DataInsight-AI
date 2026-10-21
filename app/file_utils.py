from pathlib import Path

def preparar_descargas(
    reportes: list[dict],
    carpeta_reportes: Path
) -> list[dict]:
    """
    Prepara los archivos Excel generados para
    descargarlos de forma segura.
    """

    archivos = []

    carpeta = Path(carpeta_reportes).resolve()

    for reporte in reportes:

        if not isinstance(reporte, dict):
            continue

        nombre = reporte.get("archivo")

        # Validar el nombre y la extension
        if not isinstance(nombre, str):
            continue

        if not nombre.lower().endswith(".xlsx"):
            continue

        # Construir la ruta del archivo
        ruta = (carpeta / nombre).resolve()

        # Impedir el acceso fuera de reports
        if ruta.parent != carpeta:
            continue

        if not ruta.is_file():
            continue

        # Preparar archivo para Streamlit
        archivos.append({
            "nombre": ruta.name,
            "contenido": ruta.read_bytes()
        })

    return archivos
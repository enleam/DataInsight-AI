import pytest

from app.file_utils import preparar_descargas

# ==========================================
# PRUEBA 1: ARCHIVO EXCEL VALIDO
# ==========================================

def test_descarga_excel_valido(tmp_path):

    carpeta = tmp_path / "reports"
    carpeta.mkdir()

    ruta = carpeta / "reporte_ventas.xlsx"
    ruta.write_bytes(b"contenido de prueba")

    reportes = [
        {"archivo": "reporte_ventas.xlsx"}
    ]

    archivos = preparar_descargas(
        reportes,
        carpeta
    )

    assert len(archivos) == 1

    assert archivos[0]["nombre"] == (
        "reporte_ventas.xlsx"
    )

    assert archivos[0]["contenido"] == (
        b"contenido de prueba"
    )


# ==========================================
# PRUEBA 2: VARIOS ARCHIVOS
# ==========================================

def test_descarga_varios_reportes(tmp_path):

    carpeta = tmp_path / "reports"
    carpeta.mkdir()

    (carpeta / "ventas.xlsx").write_bytes(b"ventas")
    (carpeta / "productos.xlsx").write_bytes(
        b"productos"
    )

    reportes = [
        {"archivo": "ventas.xlsx"},
        {"archivo": "productos.xlsx"}
    ]

    archivos = preparar_descargas(
        reportes,
        carpeta
    )

    assert len(archivos) == 2

    assert archivos[0]["nombre"] == "ventas.xlsx"

    assert archivos[1]["nombre"] == (
        "productos.xlsx"
    )


# ==========================================
# PRUEBA 3: ARCHIVOS NO VALIDOS
# ==========================================

def test_ignorar_archivos_invalidos(tmp_path):

    carpeta = tmp_path / "reports"
    carpeta.mkdir()

    (carpeta / "notas.txt").write_text(
        "Archivo de texto"
    )

    reportes = [
        {"archivo": "notas.txt"},
        {"archivo": "inexistente.xlsx"},
        {"archivo": None},
        {}
    ]

    archivos = preparar_descargas(
        reportes,
        carpeta
    )

    assert archivos == []


# ==========================================
# PRUEBA 4: SEGURIDAD DE RUTAS
# ==========================================

def test_bloquear_acceso_fuera_de_reports(
    tmp_path
):

    carpeta = tmp_path / "reports"
    carpeta.mkdir()

    # Archivo fuera de la carpeta autorizada
    ruta_externa = tmp_path / "privado.xlsx"
    ruta_externa.write_bytes(b"datos privados")

    reportes = [
        {"archivo": "../privado.xlsx"}
    ]

    archivos = preparar_descargas(
        reportes,
        carpeta
    )

    assert archivos == []
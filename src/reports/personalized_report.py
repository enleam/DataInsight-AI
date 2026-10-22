import logging
import re
from pathlib import Path
from uuid import uuid4

from src.database.sales_queries import (
    obtener_pedidos,
    obtener_detalle_productos
)

from src.reports.report_filters import (
    filtrar_datos_reporte
)

from src.reports.excel_generator import (
    generar_reporte_excel,
    agregar_conclusiones_ia
)

from src.agent.insights import (
    generar_conclusiones_ia
)


def generar_reporte_personalizado(
    anio: int | None = None,
    territorio: str | None = None,
    incluir_conclusiones_ia: bool = False
) -> Path:
    """
    Genera un reporte Excel personalizado.

    Permite filtrar por año y territorio y,
    opcionalmente, incorporar tres conclusiones IA
    basadas exclusivamente en los datos filtrados.
    """

    # ======================================
    # 1. VALIDAR OPCION DE IA
    # ======================================

    if not isinstance(incluir_conclusiones_ia, bool):
        raise ValueError(
            "incluir_conclusiones_ia debe ser booleano."
        )

    # ======================================
    # 2. CONSULTAR SQL SERVER
    # ======================================

    print("Consultando datos de AdventureWorks2022...")

    pedidos = obtener_pedidos()
    detalle = obtener_detalle_productos()

    # ======================================
    # 3. APLICAR FILTROS
    # ======================================

    pedidos_filtrados, detalle_filtrado = (
        filtrar_datos_reporte(
            pedidos=pedidos,
            detalle=detalle,
            anio=anio,
            territorio=territorio
        )
    )

    print(
        f"Pedidos seleccionados: "
        f"{len(pedidos_filtrados)}"
    )

    print(
        f"Lineas de productos seleccionadas: "
        f"{len(detalle_filtrado)}"
    )

    # ======================================
    # 4. GENERAR EXCEL BASE
    # ======================================

    ruta = generar_reporte_excel(
        pedidos=pedidos_filtrados,
        detalle=detalle_filtrado
    )

    if not ruta.is_file():
        raise RuntimeError(
            "No se pudo generar el archivo Excel."
        )

    # ======================================
    # 5. PERSONALIZAR NOMBRE DEL ARCHIVO
    # ======================================

    partes_nombre = []

    if anio is not None:
        partes_nombre.append(str(anio))

    if territorio is not None:

        nombre_territorio = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            territorio.strip()
        ).strip("_")

        partes_nombre.append(
            nombre_territorio or "Territorio"
        )

    if partes_nombre:

        sufijo = "_".join(partes_nombre)

        nueva_ruta = ruta.with_name(
            f"{ruta.stem}_{sufijo}{ruta.suffix}"
        )

        if nueva_ruta.exists():

            identificador = uuid4().hex[:8]

            nueva_ruta = ruta.with_name(
                f"{ruta.stem}_{sufijo}_"
                f"{identificador}{ruta.suffix}"
            )

        ruta.rename(nueva_ruta)
        ruta = nueva_ruta

    # ======================================
    # 6. INCORPORAR CONCLUSIONES IA
    # ======================================

    if incluir_conclusiones_ia:

        try:

            print(
                "Generando conclusiones IA "
                "con datos filtrados..."
            )

            # IMPORTANTE:
            # Enviamos los DataFrames filtrados,
            # no los originales.
            conclusiones = generar_conclusiones_ia(
                pedidos_filtrados,
                detalle_filtrado
            )

            agregar_conclusiones_ia(
                ruta,
                conclusiones
            )

            print(
                "Conclusiones IA incorporadas "
                "correctamente."
            )

        except Exception as error:

            # Registrar el error tecnico completo
            logging.exception(
                "Error al generar o incorporar "
                "conclusiones IA en el Excel personalizado"
            )

            # Conservar el Excel base
            print(
                "Advertencia: no se pudieron "
                "incorporar las conclusiones IA."
            )

            print(
                f"Tipo de error: "
                f"{type(error).__name__}"
            )

    # ======================================
    # 7. DEVOLVER RUTA DEL EXCEL
    # ======================================

    print(
        f"Reporte personalizado generado: {ruta}"
    )

    return ruta
import json

from google.genai import types

from src.agent.gemini_client import (
    crear_cliente_gemini,
    obtener_modelo
)

from src.agent.tools import (
    consultar_indicadores_generales,
    consultar_ventas_por_territorio,
    consultar_top_productos,
    generar_reporte_ventas,
    generar_reporte_personalizado
)

# 1. Declaraciones de herramientas

declaraciones = [
    types.FunctionDeclaration(
        name="consultar_indicadores_generales",
        description=(
            "Obtiene indicadores generales de ventas: "
            "total de pedidos, ingresos acumulados, "
            "ticket promedio y periodo disponible."
        )
    ),

    types.FunctionDeclaration(
        name="consultar_ventas_por_territorio",
        description=(
            "Obtiene un ranking de territorios "
            "comerciales por ingresos."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "limite": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": (
                        "Cantidad de territorios."
                    )
                }
            },
            "required": ["limite"]
        }
    ),

    types.FunctionDeclaration(
        name="consultar_top_productos",
        description=(
            "Obtiene los productos con mayores "
            "ingresos o mayor cantidad de unidades "
            "vendidas. Utiliza ingresos si el usuario "
            "pregunta por facturacion o ventas monetarias."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "limite": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10
                },
                "criterio": {
                    "type": "string",
                    "enum": ["ingresos", "unidades"],
                    "description": (
                        "Ordenar por ingresos monetarios "
                        "o cantidad de unidades vendidas."
                    )
                }
            },
            "required": ["limite", "criterio"]
        }
    )
]

# Herramienta 4: generacion de reportes Excel
declaraciones.append(
    types.FunctionDeclaration(
        name="generar_reporte_ventas",
        description=(
            "Genera un reporte Excel (.xlsx) completo "
            "de ventas de AdventureWorks2022. "
            "El reporte contiene cinco hojas base: "
            "Resumen, Ventas mensuales, Territorios, "
            "Top ingresos y Top unidades. "
            "Adicionalmente, puede incluir una sexta "
            "hoja llamada Conclusiones IA, con tres "
            "conclusiones empresariales generadas "
            "mediante Gemini. "
            "Incluye dos graficos de ventas. "
            "Utiliza esta herramienta solamente cuando "
            "el usuario solicite generar, crear o "
            "exportar un reporte Excel. "
            "No requiere argumentos."
        )
    )
)

# Herramienta 5: reportes personalizados
declaraciones.append(
    types.FunctionDeclaration(
        name="generar_reporte_personalizado",
        description=(
            "Genera un archivo Excel de ventas "
            "personalizado para AdventureWorks2022. "
            "Utilizar cuando el usuario solicite "
            "un reporte Excel filtrado por año, "
            "territorio o ambos. "
            "Requiere al menos un filtro: "
            "anio o territorio. "
            "Si solicita conclusiones de IA, "
            "establecer incluir_conclusiones_ia "
            "en true. En caso contrario, false. "
            "El reporte tiene cinco hojas base, "
            "dos graficos y una sexta hoja "
            "opcional de Conclusiones IA. "
            "No usar para simples consultas "
            "sin solicitud de archivo."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "anio": types.Schema(
                    type="INTEGER",
                    description=(
                        "Año calendario solicitado, "
                        "por ejemplo 2013."
                    )
                ),
                "territorio": types.Schema(
                    type="STRING",
                    description=(
                        "Nombre del territorio, "
                        "por ejemplo Canada "
                        "o Southwest."
                    )
                ),
                "incluir_conclusiones_ia": types.Schema(
                    type="BOOLEAN",
                    description=(
                        "True solamente cuando "
                        "el usuario solicite "
                        "conclusiones de IA."
                    )
                )
            }
        )
    )
)

herramienta = types.Tool(
    function_declarations=declaraciones
)

# 2. Ejecucion controlada

def ejecutar_herramienta(nombre: str, argumentos: dict):

    # 1. Generar reporte Excel
    if nombre == "generar_reporte_ventas":

        if argumentos:
            raise ValueError(
                "La generacion del reporte no admite argumentos."
            )

        return generar_reporte_ventas()

    # 2. Consultar indicadores generales
    elif nombre == "consultar_indicadores_generales":

        if argumentos:
            raise ValueError(
                "Argumentos no permitidos."
            )

        return consultar_indicadores_generales()

    # 3. Consultar ventas por territorio
    elif nombre == "consultar_ventas_por_territorio":

        if set(argumentos) != {"limite"}:
            raise ValueError(
                "Argumentos no validos."
            )

        return consultar_ventas_por_territorio(
            limite=argumentos["limite"]
        )

    # 4. Consultar productos
    elif nombre == "consultar_top_productos":

        if set(argumentos) != {"limite", "criterio"}:
            raise ValueError(
                "Argumentos no validos."
            )

        return consultar_top_productos(
            limite=argumentos["limite"],
            criterio=argumentos["criterio"]
        )

    elif nombre == "generar_reporte_personalizado":

        permitidos = {
            "anio",
            "territorio",
            "incluir_conclusiones_ia"
        }

        if not set(argumentos).issubset(permitidos):
            raise ValueError(
                "Argumentos no validos para "
                "el reporte personalizado."
            )

        return generar_reporte_personalizado(
            **argumentos
        )

    # 5. Rechazar funciones no autorizadas
    else:
        raise ValueError(
            f"Herramienta no autorizada: {nombre}"
        )


# 3. Agente principal
def preguntar_agente(pregunta: str, on_reporte=None) -> str:
    """Procesa preguntas con multiples herramientas."""

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacia.")

    instrucciones = """
    Eres DataInsight AI, un analista de datos empresarial
    especializado en AdventureWorks2022.

    REGLAS:
    - Responde siempre en español.
    - Utiliza herramientas para obtener datos reales.
    - Nunca inventes cifras ni monedas.
    - Distingue hechos de interpretaciones.
    - No atribuyas causalidad sin evidencia.
    - No supongas que todos los años estan completos.
    - SubTotal representa ingresos de productos
      antes de impuestos y transporte.
    - Los rankings de productos usan LineTotal.
    - Las conclusiones sobre un Top N solamente
      describen el conjunto consultado.

    USO DE HERRAMIENTAS:
    - Si necesitas indicadores generales, consulta KPIs.
    - Si necesitas territorios, consulta territorios.
    - Si necesitas productos, consulta productos.
    - Si una pregunta necesita varias herramientas,
      solicita todas las necesarias.
    - Puedes solicitar varias funciones en una llamada
      o solicitar funciones adicionales despues de
      recibir resultados anteriores.

    VALIDACION DE CONCLUSIONES:
    - No confundas ingresos con cantidad de pedidos
      ni con unidades vendidas.
    - Un ranking ordenado por ingresos no demuestra
      que sus integrantes tengan el mayor volumen
      de pedidos de toda la empresa.
    - No extrapoles un Top N al catalogo completo.
    - No afirmes recompra, fidelidad, rentabilidad,
      preferencias ni causas sin datos que lo prueben.
    - Si calculas un porcentaje, especifica claramente
      el numerador, el denominador y el periodo.
    - Si la informacion disponible es insuficiente,
      indica que no se puede determinar.
    - Cuando compares dos indicadores, verifica que
      correspondan al mismo periodo de analisis.

    GENERACION DE REPORTES:
    - No afirmes que un archivo fue generado hasta
      recibir la confirmacion de la herramienta.
    - Indica el nombre exacto del archivo y que
      esta guardado en la carpeta local reports.
    - No inventes enlaces de descarga.
    - Consulta el campo conclusiones_ia_en_excel
      para confirmar si se incorporaron conclusiones.
    - Si hay seis hojas, informa que se incluye
      la hoja Conclusiones IA.
    - Si hay cinco hojas, no afirmes que incluye
      conclusiones de Gemini.
    - No generes reportes si el usuario solamente
      solicita consultar informacion.
    - Si el usuario solicita un Excel sin filtros,
      utiliza generar_reporte_ventas.
    - Si solicita un Excel por año, territorio o
      ambos, utiliza generar_reporte_personalizado.
    - Nunca utilices el reporte general para una
      solicitud que incluye filtros.
    - No inventes un año o territorio que el
      usuario no haya indicado.
    - Si el usuario solicita conclusiones de IA
      en el reporte personalizado, establece
      incluir_conclusiones_ia en true.
    - Comprueba conclusiones_ia_en_excel antes
      de afirmar que el archivo contiene IA.
    - Si existe una advertencia de generación,
      comunícala al usuario.
    - No afirmes que generaste un archivo hasta
      recibir la confirmación de la herramienta.

    Presenta tablas cuando sean utiles y termina
    con conclusiones empresariales breves.
    """

    historial = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=pregunta)
            ]
        )
    ]

    max_rondas = 3
    max_ejecuciones = 6
    total_ejecuciones = 0
    cache_reportes = {}

    with crear_cliente_gemini() as cliente:

        modelo = obtener_modelo()

        for ronda in range(max_rondas):

            # Primera ronda: exigir una herramienta.
            # Rondas siguientes: permitir respuesta
            # final o nuevas herramientas.
            modo = "ANY" if ronda == 0 else "AUTO"

            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=historial,
                config=types.GenerateContentConfig(
                    system_instruction=instrucciones,
                    tools=[herramienta],
                    tool_config=types.ToolConfig(
                        function_calling_config=(
                            types.FunctionCallingConfig(
                                mode=modo
                            )
                        )
                    )
                )
            )

            llamadas = respuesta.function_calls or []

            # Gemini ya puede responder sin mas herramientas
            if not llamadas:

                if respuesta.text:
                    return respuesta.text

                raise RuntimeError(
                    "Gemini no devolvio una respuesta valida."
                )

            if not respuesta.candidates:
                raise RuntimeError(
                    "Gemini no devolvio contenido valido."
                )

            if total_ejecuciones + len(llamadas) > max_ejecuciones:
                raise RuntimeError(
                    "Se alcanzo el limite de herramientas."
                )

            # Conservar el contenido original del modelo
            historial.append(
                respuesta.candidates[0].content
            )

            partes_respuesta = []

            print(f"\n=== RONDA {ronda + 1} ===")


            # Ejecutar todas las herramientas solicitadas
            for llamada in llamadas:

                nombre = llamada.name
                argumentos = dict(llamada.args or {})

                print(f"\nHerramienta: {nombre}")
                print(f"Argumentos: {argumentos}")

                # 1. Identificar herramientas de reportes
                es_reporte = nombre in {
                    "generar_reporte_ventas",
                    "generar_reporte_personalizado"
                }

                # 2. Ejecutar reportes con cache
                if es_reporte:

                    clave = (
                        nombre,
                        json.dumps(
                            argumentos,
                            sort_keys=True,
                            ensure_ascii=False
                        )
                    )

                    if clave in cache_reportes:

                        resultado = cache_reportes[clave]

                    else:

                        resultado = ejecutar_herramienta(
                            nombre,
                            argumentos
                        )

                        cache_reportes[clave] = resultado

                        # Notificar el archivo a Streamlit
                        if (
                            on_reporte is not None
                            and resultado.get("estado") == "generado"
                        ):
                            on_reporte(resultado)

                # 3. Ejecutar herramientas de consulta
                else:

                    resultado = ejecutar_herramienta(
                        nombre,
                        argumentos
                    )

                # 4. Actualizar contador
                total_ejecuciones += 1

                print("Analisis completado correctamente.")

                # 5. Preparar resultado para Gemini
                parte = types.Part.from_function_response(
                    name=nombre,
                    response={"resultado": resultado}
                )

                partes_respuesta.append(parte)

            # Enviar todos los resultados al modelo
            historial.append(
                types.Content(
                    role="user",
                    parts=partes_respuesta
                )
            )

        # Se llego al maximo de rondas.
        # Solicitar una respuesta sin mas herramientas.
        respuesta_final = cliente.models.generate_content(
            model=modelo,
            contents=historial,
            config=types.GenerateContentConfig(
                system_instruction=instrucciones,
                tools=[herramienta],
                tool_config=types.ToolConfig(
                    function_calling_config=(
                        types.FunctionCallingConfig(
                            mode="NONE"
                        )
                    )
                )
            )
        )

        if not respuesta_final.text:
            raise RuntimeError(
                "Gemini no genero una respuesta final."
            )

        return respuesta_final.text

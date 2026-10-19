from google.genai import types

from src.agent.gemini_client import (
    crear_cliente_gemini,
    obtener_modelo
)

from src.agent.tools import (
    consultar_indicadores_generales,
    consultar_ventas_por_territorio,
    consultar_top_productos
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

herramienta = types.Tool(
    function_declarations=declaraciones
)


# 2. Ejecucion controlada

def ejecutar_herramienta(nombre: str, argumentos: dict):

    if nombre == "consultar_indicadores_generales":

        if argumentos:
            raise ValueError("Argumentos no permitidos.")

        return consultar_indicadores_generales()

    elif nombre == "consultar_ventas_por_territorio":

        if set(argumentos) != {"limite"}:
            raise ValueError("Argumentos no validos.")

        return consultar_ventas_por_territorio(
            limite=argumentos["limite"]
        )

    elif nombre == "consultar_top_productos":

        if set(argumentos) != {"limite", "criterio"}:
            raise ValueError("Argumentos no validos.")

        return consultar_top_productos(
            limite=argumentos["limite"],
            criterio=argumentos["criterio"]
        )

    else:
        raise ValueError(
            f"Herramienta no autorizada: {nombre}"
        )


# 3. Agente principal


def preguntar_agente(pregunta: str) -> str:
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

                # Solo ejecutar herramientas autorizadas
                resultado = ejecutar_herramienta(
                    nombre,
                    argumentos
                )

                total_ejecuciones += 1

                print("Analisis completado correctamente.")

                # Convertir resultado para Gemini
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

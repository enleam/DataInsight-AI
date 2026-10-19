from src.agent.gemini_client import (
    crear_cliente_gemini,
    obtener_modelo
)


def main():

    print("=== DATAINSIGHT AI ===")
    print("Sprint 3 - Prueba de Gemini\n")

    modelo = obtener_modelo()

    print(f"Modelo configurado: {modelo}")
    print("Enviando solicitud a Gemini...\n")

    # Crear y cerrar correctamente el cliente
    with crear_cliente_gemini() as cliente:

        respuesta = cliente.models.generate_content(
            model=modelo,
            contents=(
                "Responde en español y en un máximo "
                "de 3 oraciones. Explica qué es un "
                "indicador KPI en análisis de ventas "
                "y proporciona un ejemplo."
            )
        )

        if not respuesta.text:
            raise RuntimeError(
                "Gemini no devolvio una respuesta de texto."
            )

        print("=== RESPUESTA DE GEMINI ===")
        print(respuesta.text)


if __name__ == "__main__":
    main()
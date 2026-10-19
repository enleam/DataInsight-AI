import traceback

from src.agent.gemini_agent import preguntar_agente

def main():

    print("=== DATAINSIGHT AI ===")
    print("Sprint 3 - Agente inteligente con Gemini")
    print("Analisis de ventas por territorio\n")

    while True:

        pregunta = input(
            "\nEscribe tu pregunta (o 'salir'): "
        ).strip()

        if pregunta.lower() == "salir":
            print("Finalizando DataInsight AI...")
            break

        if not pregunta:
            continue

        try:
            respuesta = preguntar_agente(pregunta)

            print("\n=== RESPUESTA DE DATAINSIGHT AI ===")
            print(respuesta)

        except Exception as error:
            print("\nNo se pudo procesar la solicitud.")
            print(f"Tipo de error: {type(error).__name__}")
            print(f"Detalle: {error}")

            print("\n=== DETALLE TECNICO ===")
            traceback.print_exc()


if __name__ == "__main__":
    main()
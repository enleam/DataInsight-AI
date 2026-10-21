import pandas as pd
import plotly.express as px
import streamlit as st

from src.database.sales_queries import obtener_pedidos

from src.analytics.sales_analysis import (
    preparar_pedidos,
    calcular_kpis
)


def cargar_datos_dashboard():
    """
    Consulta SQL Server y prepara los indicadores
    para mostrarlos en Streamlit.
    """

    # 1. Consultar los pedidos
    pedidos = obtener_pedidos()

    if pedidos.empty:
        raise ValueError(
            "No se encontraron pedidos en SQL Server."
        )

    # 2. Preparar datos con Pandas
    pedidos = preparar_pedidos(pedidos).copy()

    pedidos["OrderDate"] = pd.to_datetime(
        pedidos["OrderDate"]
    )

    pedidos["SubTotal"] = pd.to_numeric(
        pedidos["SubTotal"]
    )

    # 3. Calcular KPIs con nuestro modulo existente
    kpis = calcular_kpis(pedidos)

    # 4. Agrupar ventas por mes
    ventas_mensuales = (
        pedidos.assign(
            Mes=pedidos["OrderDate"].dt.to_period("M")
        )
        .groupby("Mes", as_index=False)["SubTotal"]
        .sum()
        .rename(columns={"SubTotal": "Ventas"})
        .sort_values("Mes")
    )

    ventas_mensuales["Mes"] = (
        ventas_mensuales["Mes"].dt.to_timestamp()
    )

    # 5. Agrupar ventas por territorio
    territorios = (
        pedidos.groupby(
            "Territorio",
            as_index=False,
            dropna=False
        )
        .agg(
            Ventas=("SubTotal", "sum"),
            Pedidos=("SalesOrderID", "nunique")
        )
        .sort_values("Ventas", ascending=True)
    )

    territorios["Territorio"] = (
        territorios["Territorio"].fillna(
            "Sin territorio"
        )
    )

    # 6. Devolver los resultados
    return {
        "kpis": kpis,
        "ventas_mensuales": ventas_mensuales,
        "territorios": territorios
    }


def mostrar_dashboard():
    """
    Renderiza indicadores y graficos interactivos.
    """

    with st.expander(
        "📈 Dashboard de ventas",
        expanded=True
    ):

        st.caption(
            "Indicadores calculados directamente "
            "desde AdventureWorks2022."
        )

        # 1. Boton de carga y actualizacion
        if st.button(
            "🔄 Cargar / actualizar indicadores",
            key="actualizar_dashboard"
        ):

            try:
                with st.spinner(
                    "Consultando ventas de SQL Server..."
                ):

                    datos = cargar_datos_dashboard()

                    st.session_state[
                        "datos_dashboard"
                    ] = datos

                st.success(
                    "Indicadores actualizados correctamente."
                )

            except Exception as error:

                st.error(
                    "No se pudieron cargar los datos. "
                    f"Detalle: {type(error).__name__}: {error}"
                )

        # 2. Recuperar datos de esta sesion
        datos = st.session_state.get(
            "datos_dashboard"
        )

        if datos is None:
            st.info(
                "Presiona el boton para cargar "
                "los indicadores de ventas."
            )
            return

        kpis = datos["kpis"]

        # 3. Mostrar KPIs
        columna1, columna2, columna3 = st.columns(3)

        with columna1:
            st.metric(
                "Ventas por productos (SubTotal)",
                f"{float(kpis['total_ventas']):,.2f}"
            )

        with columna2:
            st.metric(
                "Total de pedidos",
                f"{int(kpis['total_pedidos']):,}"
            )

        with columna3:
            st.metric(
                "Ticket promedio",
                f"{float(kpis['ticket_promedio']):,.2f}"
            )

        inicio = pd.to_datetime(
            kpis["primera_fecha"]
        ).strftime("%d/%m/%Y")

        fin = pd.to_datetime(
            kpis["ultima_fecha"]
        ).strftime("%d/%m/%Y")

        st.caption(
            f"Periodo analizado: {inicio} al {fin}. "
            "Ingresos antes de impuestos y fletes. "
            "No se especifica moneda."
        )

        st.divider()

        # 4. Graficos interactivos
        grafico1, grafico2 = st.columns(2)

        with grafico1:

            fig_mensual = px.line(
                datos["ventas_mensuales"],
                x="Mes",
                y="Ventas",
                markers=True,
                title="Evolucion mensual de ventas",
                labels={
                    "Mes": "Mes",
                    "Ventas": "Ingresos por productos"
                }
            )

            fig_mensual.update_layout(
                height=420
            )

            st.plotly_chart(
                fig_mensual,
                use_container_width=True
            )

        with grafico2:

            fig_territorios = px.bar(
                datos["territorios"],
                x="Ventas",
                y="Territorio",
                orientation="h",
                title="Ingresos por territorio",
                hover_data=["Pedidos"],
                labels={
                    "Ventas": "Ingresos por productos",
                    "Territorio": "Territorio"
                }
            )

            fig_territorios.update_layout(
                height=420
            )

            st.plotly_chart(
                fig_territorios,
                use_container_width=True
            )
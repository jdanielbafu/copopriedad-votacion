import streamlit as st
import plotly.express as px
import pandas as pd

from services.sheets_service import (
    load_responses,
    load_coefficients
)

from services.calculations import process_votes, calculate_quorum

st.set_page_config(
    page_title="Votación PH",
    layout="wide"
)

st.title("Sistema de Votación PH")


@st.fragment(run_every=10)
def mostrar_resultados():
    df_votes = load_responses()
    df_coef = load_coefficients()

    quorum_pct = calculate_quorum(df_coef)
    if quorum_pct is not None:
        quorum_met = quorum_pct >= 50
        st.subheader("Quorum de la Asamblea")
        qcol1, qcol2 = st.columns([1, 4])
        with qcol1:
            st.metric("Quorum", f"{quorum_pct}%")
        with qcol2:
            if quorum_met:
                st.success(f"Quorum alcanzado — {quorum_pct}% del coeficiente total está presente (mínimo 50%)")
            else:
                st.error(f"Sin quorum — {quorum_pct}% presente, se requiere al menos 50% del coeficiente total")
        st.divider()

    if df_votes.empty:
        st.info("Aún no hay votos registrados. La página se actualizará automáticamente.")
        return

    try:
        resultados = process_votes(df_votes, df_coef)
    except KeyError as exc:
        st.error(f"Error al procesar los votos: {exc}")
        st.write("Revisa los nombres de columnas en las pestañas 'respuestas' y 'coeficientes'.")
        st.write("Columnas actuales en respuestas:", list(df_votes.columns))
        st.write("Columnas actuales en coeficientes:", list(df_coef.columns))
        return

    st.subheader("Porcentaje de la participación")
    col4 = st.columns(1)
    col4[0].metric("Participación", f"{resultados['participacion_pct']}%")
    
    st.subheader("Resultados de la Votación")
    col1, col2, col3 = st.columns(3)

    col1.metric("Opción A", f"{resultados['Opción A']}%")
    col2.metric("Opción B", f"{resultados['Opción B']}%")
    col3.metric("Opción C", f"{resultados['Opción C']}%")
    


    chart_df = pd.DataFrame({
        "Resultado": ["Opción A", "Opción B", "Opción C"],
        "Porcentaje": [
            resultados["Opción A"],
            resultados["Opción B"],
            resultados["Opción C"]
        ]
    })

    fig = px.pie(
        chart_df,
        values="Porcentaje",
        names="Resultado",
        title="Distribución de Votos"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(resultados["df_votos"])


mostrar_resultados()

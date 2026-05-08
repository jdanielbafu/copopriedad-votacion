import streamlit as st
import plotly.express as px
import pandas as pd

from services.sheets_service import (
    load_responses,
    load_coefficients
)

from services.calculations import process_votes

st.set_page_config(
    page_title="Votación PH",
    layout="wide"
)

st.title("Sistema de Votación PH")


@st.fragment(run_every=10)
def mostrar_resultados():
    df_votes = load_responses()
    df_coef = load_coefficients()

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

    quorum_pct = resultados.get("quorum_pct")
    if quorum_pct is not None:
        quorum_met = quorum_pct >= 51
        st.subheader("Quorum de la Asamblea")
        qcol1, qcol2 = st.columns([1, 4])
        with qcol1:
            st.metric("Quorum", f"{quorum_pct}%")
        with qcol2:
            if quorum_met:
                st.success(f"Quorum alcanzado — {quorum_pct}% del coeficiente total está presente (mínimo 51%)")
            else:
                st.error(f"Sin quorum — {quorum_pct}% presente, se requiere al menos 51% del coeficiente total")
        st.divider()

    st.subheader("Resultados de la Votación")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("A Favor", f"{resultados['favor_pct']}%")
    col2.metric("En Contra", f"{resultados['contra_pct']}%")
    col3.metric("Blanco", f"{resultados['blanco_pct']}%")
    col4.metric("Participación", f"{resultados['participacion_pct']}%")

    chart_df = pd.DataFrame({
        "Resultado": ["Favor", "Contra", "Blanco"],
        "Porcentaje": [
            resultados["favor_pct"],
            resultados["contra_pct"],
            resultados["blanco_pct"]
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

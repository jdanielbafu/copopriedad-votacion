import pandas as pd


def validate_columns(df: pd.DataFrame, required_columns: list, df_name: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise KeyError(
            f"El dataframe '{df_name}' no tiene las columnas esperadas: {missing}. "
            f"Columnas disponibles: {list(df.columns)}"
        )


def _is_attending(val) -> bool:
    if isinstance(val, bool):
        return val
    text = str(val).strip().lower()
    return text in {"1", "true", "si", "sí", "yes", "x", "verdadero"}


def calculate_quorum(df_coef) -> float | None:
    df_coef = df_coef.copy()
    df_coef["coeficiente"] = pd.to_numeric(df_coef["coeficiente"], errors="coerce").fillna(0)
    total_coef = df_coef["coeficiente"].sum()
    if total_coef == 0 or "asistencia" not in df_coef.columns:
        return None
    attending_mask = df_coef["asistencia"].apply(_is_attending)
    quorum_coef = df_coef.loc[attending_mask, "coeficiente"].sum()
    return round((quorum_coef / total_coef) * 100, 2)


def process_votes(df_votes, df_coef):
    validate_columns(df_votes, ["apartamento", "voto"], "df_votes")
    validate_columns(df_coef, ["apartamento", "coeficiente"], "df_coef")

    df_votes = df_votes.copy()
    df_coef = df_coef.copy()

    df_votes["apartamento"] = df_votes["apartamento"].astype(str).str.strip()
    df_coef["apartamento"] = df_coef["apartamento"].astype(str).str.strip()
    df_votes["voto"] = df_votes["voto"].astype(str).str.strip()
    df_coef["coeficiente"] = pd.to_numeric(df_coef["coeficiente"], errors="coerce").fillna(0)

    if "timestamp" in df_votes.columns:
        df_votes = df_votes.sort_values("timestamp")

    df_votes = df_votes.drop_duplicates(subset=["apartamento"], keep="last")

    df = df_votes.merge(
        df_coef,
        on="apartamento",
        how="left"
    )

    total_coef = df_coef["coeficiente"].sum()

    if total_coef == 0:
        raise ValueError("El total de coeficientes es 0. Revisa los datos de la hoja 'coeficientes'.")

    favor = df[df["voto"] == "Favor"]["coeficiente"].sum()

    contra = df[df["voto"] == "Contra"]["coeficiente"].sum()

    blanco = df[df["voto"] == "Blanco"]["coeficiente"].sum()

    participacion = df["coeficiente"].sum()

    resultados = {
        "favor_pct": round((favor / total_coef) * 100, 2),
        "contra_pct": round((contra / total_coef) * 100, 2),
        "blanco_pct": round((blanco / total_coef) * 100, 2),
        "participacion_pct": round((participacion / total_coef) * 100, 2),
        "quorum_pct": None,
        "df_votos": df_votes,
    }

    if "asistencia" in df_coef.columns:
        attending_mask = df_coef["asistencia"].apply(_is_attending)
        quorum_coef = df_coef.loc[attending_mask, "coeficiente"].sum()
        resultados["quorum_pct"] = round((quorum_coef / total_coef) * 100, 2)

    return resultados
import streamlit as st
import pandas as pd
import gspread
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def connect_sheet():

    creds_dict = st.secrets["gcp_service_account"]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict,
        scope
    )

    client = gspread.authorize(creds)

    spreadsheet_name = st.secrets["google"]["sheet_name"]

    try:
        sheet = client.open(spreadsheet_name)
        return sheet
    except SpreadsheetNotFound as exc:
        fallback_message = []

        try:
            spreadsheets = client.openall()
            titles = [s.title for s in spreadsheets]
            fallback_message.append("Hojas accesibles:")
            fallback_message.extend([f"- {title}" for title in titles[:20]])
        except Exception:
            fallback_message.append("No se pudo listar hojas accesibles.")

        message = (
            f"No se encontró el spreadsheet '{spreadsheet_name}'.\n"
            "1. Verifica que el nombre exacto del spreadsheet sea correcto.\n"
            "2. Asegúrate de que la cuenta de servicio esté compartida con ese archivo.\n"
            "3. Si el valor en secrets es una URL o ID, usa solo el ID.\n\n"
            + "\n".join(fallback_message)
        )

        raise RuntimeError(message) from exc

def _get_worksheet(sheet, names):
    for name in names:
        try:
            return sheet.worksheet(name)
        except WorksheetNotFound:
            continue
    raise WorksheetNotFound(
        f"No se encontró ninguna de las hojas: {names}."
    )


def _normalize_text(text: str) -> str:
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "¿": "",
        "?": "",
    }
    normalized = text.strip().lower()
    for original, replacement in replacements.items():
        normalized = normalized.replace(original, replacement)
    return normalized


def _normalize_response_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        normalized = _normalize_text(col)
        if "apartamento" in normalized and "interior" in normalized:
            rename_map[col] = "apartamento"
        elif "aprueba" in normalized and "presupuesto" in normalized:
            rename_map[col] = "voto"
    return df.rename(columns=rename_map)


def _normalize_vote_values(df: pd.DataFrame) -> pd.DataFrame:
    if "voto" not in df.columns:
        return df

    def map_vote(value):
        if pd.isna(value):
            return "Blanco"
        text = str(value).strip().lower()
        text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        if text in {"si", "sí", "s"}:
            return "Favor"
        if text in {"no", "n"}:
            return "Contra"
        if text == "":
            return "Blanco"
        if "blanco" in text:
            return "Blanco"
        return value

    df["voto"] = df["voto"].apply(map_vote)
    return df


@st.cache_data(ttl=10)
def load_responses():

    sheet = connect_sheet()

    worksheet = _get_worksheet(sheet, ["respuestas", "Respuestas"])

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)
    df = _normalize_response_columns(df)
    df = _normalize_vote_values(df)

    return df


@st.cache_data(ttl=10)
def load_coefficients():

    sheet = connect_sheet()

    worksheet = sheet.worksheet("coeficientes")

    data = worksheet.get_all_records()

    return pd.DataFrame(data)
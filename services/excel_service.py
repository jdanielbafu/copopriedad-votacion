import streamlit as st
import pandas as pd

def load_responses():
    # Asumiendo que hay un archivo Excel llamado respuestas.xlsx en el directorio
    # Cambia la ruta si es necesario
    df = pd.read_excel("respuestas.xlsx")
    return df

def load_coefficients():
    # Asumiendo que hay un archivo Excel llamado coeficientes.xlsx en el directorio
    # Cambia la ruta si es necesario
    df = pd.read_excel("coeficientes.xlsx")
    return df
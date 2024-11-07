import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import streamlit as st

# Inizializza il modello GPT-4o-mini
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Definisci i prompt per ogni assistente specifico
prompt_preventivo_auto = PromptTemplate(
    input_variables=["targa", "tipo_polizza", "garanzie_opzionali"],
    template="Stai raccogliendo i dati per un preventivo auto per il veicolo con targa {targa}..."
)
prompt_preventivo_casa = PromptTemplate(
    input_variables=["dati_casa", "garanzie_opzionali"],
    template="Stai raccogliendo i dati per un preventivo casa per la proprietà: {dati_casa}..."
)
prompt_preventivo_infortuni = PromptTemplate(
    input_variables=["dati_infortunio", "copertura_opzionale"],
    template="Stai raccogliendo i dati per una polizza infortuni per il cliente..."
)
prompt_preventivo_salute = PromptTemplate(
    input_variables=["dati_salute"],
    template="Stai raccogliendo i dati per una polizza salute per il cliente..."
)
prompt_gestione_sinistri = PromptTemplate(
    input_variables=["dati_sinistro"],
    template="Stai raccogliendo i dati per la gestione del sinistro: {dati_sinistro}..."
)

# Inizializza le catene per ogni assistente
preventivo_auto_chain = prompt_preventivo_auto | llm
preventivo_casa_chain = prompt_preventivo_casa | llm
preventivo_infortuni_chain = prompt_preventivo_infortuni | llm
preventivo_salute_chain = prompt_preventivo_salute | llm
gestione_sinistri_chain = prompt_gestione_sinistri | llm

# Interfaccia grafica in Streamlit
st.title("Assistente Assicurativo di Assistudio Vigevano")
st.subheader(
    "Benvenuto nel nostro assistente virtuale. Siamo qui per aiutarti con le tue esigenze assicurative.")

# Selezione del tipo di assistenza
richiesta_generale = st.text_input("Inserisci la tua richiesta qui:")
if st.button("Invia richiesta"):
    # Instradamento delle richieste
    instradamento_chain = PromptTemplate(
        input_variables=["richiesta_cliente"],
        template="Instrada la richiesta del cliente in base alla seguente domanda: '{richiesta_cliente}'..."
    ) | llm
    risposta_instradamento = instradamento_chain.invoke(
        {"richiesta_cliente": richiesta_generale})
    decisione = risposta_instradamento.content.strip().lower()

    if decisione == "auto":
        st.write("Connettendo all'assistente specializzato per auto...")
        targa = st.text_input("Inserisci la targa del veicolo:")
        tipo_polizza = st.selectbox("Questa è una polizza nuova o trasferita?", [
                                    "Nuova", "Trasferita"])
        if tipo_polizza == "Nuova":
            classe_rischio = st.selectbox("Parti in classe 14 o con attestato di rischio?", [
                                          "Classe 14", "Altra targa"])
            tipo_polizza += f" ({classe_rischio})"
        garanzie_opzionali = st.multiselect("Seleziona le garanzie opzionali:", [
            "Assistenza", "Cristalli", "Tutela Legale", "Incendio", "Furto",
            "Atti Vandalici", "Fenomeni Naturali", "Infortuni del Conducente",
            "Garanzie Aggiuntive", "Kasko", "Collisione"
        ])
        if st.button("Genera Preventivo"):
            garanzie_opzionali_str = ", ".join(
                garanzie_opzionali) if garanzie_opzionali else "nessuna garanzia opzionale"
            risposta_preventivo = preventivo_auto_chain.invoke({
                "targa": targa,
                "tipo_polizza": tipo_polizza,
                "garanzie_opzionali": garanzie_opzionali_str
            })
            st.write("Conferma del preventivo auto:",
                     risposta_preventivo.content)

    elif decisione == "casa":
        st.write("Connettendo all'assistente specializzato per casa...")
        dati_casa = st.text_area("Descrivi l'immobile e la sua posizione:")
        garanzie_opzionali = st.multiselect("Seleziona le garanzie opzionali per la casa:", [
            "Incendio", "Furto", "Atti vandalici", "Fenomeni naturali", "Danni da acqua"
        ])
        if st.button("Genera Preventivo Casa"):
            garanzie_opzionali_str = ", ".join(
                garanzie_opzionali) if garanzie_opzionali else "nessuna garanzia opzionale"
            risposta_preventivo_casa = preventivo_casa_chain.invoke({
                "dati_casa": dati_casa,
                "garanzie_opzionali": garanzie_opzionali_str
            })
            st.write("Conferma del preventivo casa:",
                     risposta_preventivo_casa.content)

    elif decisione == "infortuni":
        st.write("Connettendo all'assistente specializzato per infortuni...")
        dati_infortunio = st.text_input(
            "Descrivi brevemente la tua attività e i rischi associati:")
        copertura_opzionale = st.multiselect("Seleziona le coperture opzionali:", [
                                             "Infortuni", "Invalidità", "Decesso"])
        if st.button("Genera Preventivo Infortuni"):
            copertura_opzionale_str = ", ".join(
                copertura_opzionale) if copertura_opzionale else "nessuna copertura opzionale"
            risposta_preventivo_infortuni = preventivo_infortuni_chain.invoke({
                "dati_infortunio": dati_infortunio,
                "copertura_opzionale": copertura_opzionale_str
            })
            st.write("Conferma del preventivo infortuni:",
                     risposta_preventivo_infortuni.content)

    elif decisione == "salute":
        st.write("Connettendo all'assistente specializzato per salute...")
        dati_salute = st.text_input(
            "Descrivi eventuali condizioni mediche preesistenti o richieste specifiche:")
        if st.button("Genera Preventivo Salute"):
            risposta_preventivo_salute = preventivo_salute_chain.invoke(
                {"dati_salute": dati_salute})
            st.write("Conferma del preventivo salute:",
                     risposta_preventivo_salute.content)

    elif decisione == "sinistri":
        st.write("Connettendo all'assistente specializzato per sinistri...")
        dati_sinistro = st.text_area(
            "Descrivi i dettagli del sinistro o della richiesta:")
        if st.button("Gestisci Sinistro"):
            risposta_gestione_sinistri = gestione_sinistri_chain.invoke(
                {"dati_sinistro": dati_sinistro})
            st.write("Conferma della gestione del sinistro:",
                     risposta_gestione_sinistri.content)

    else:
        st.write(
            "Non sono riuscito a determinare l'assistenza corretta. Prova con maggiori dettagli.")

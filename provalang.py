import os
from langchain_openai import ChatOpenAI
from langchain import LLMChain, PromptTemplate
from langchain.chains import SimpleSequentialChain

# Inizializza il modello GPT-4o-mini
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Interazione iniziale con il cliente
print("Benvenuto in Assistudio Vigevano! Inserisci i dati richiesti per poterti mettere in contatto con il nostro agente virtuale.")
nome = input("Inserisci il tuo nome e cognome: ")
età = input("Inserisci la tua età: ")
cliente = input("Sei già cliente di Assistudio Vigevano? (sì/no): ")

# Verifica se è un cliente esistente
if cliente.lower() == "sì":
    tipo_servizio = input(
        "Per favore, indica quale servizio desideri tra:\n"
        "- Preventivo auto\n"
        "- Preventivo casa\n"
        "- Preventivo infortuni\n"
        "- Preventivo salute\n"
        "- Preventivo impresa\n"
        "- Denuncia sinistro\n"
        "- Richiesta su sinistro\n"
        "- Richiesta informazioni aggiuntive\n"
        "Risposta: "
    )
    identificativo = input("Per procedere, indica il tuo codice fiscale: ")
else:
    tipo_servizio = "censimento anagrafico"
    identificativo = "N/A"

# Crea un input unico per il primo agente
dati_cliente = f"Nome: {nome}, Età: {età}, Cliente esistente: {cliente}, Tipo di servizio: {tipo_servizio}, Identificativo: {identificativo}"

# Definisci il prompt per l'agente di front office
prompt_front_office = PromptTemplate(
    input_variables=["dati_cliente"],
    template=(
        "Sei il front office di un ufficio di assicurazioni che si chiama Assistudio Vigevano. "
        "Un cliente ha fornito i seguenti dettagli:\n{dati_cliente}\n"
        "Indirizza il cliente comunque alla sede in Corso Pavia, 71/5 a Vigevano o digli di chiamare il 038174441 se qualcosa va storto in questa richiesta. Non essere troppo formale nelle risposte."
    )
)
agente_front_office = LLMChain(llm=llm, prompt=prompt_front_office)

# Esegui il primo agente (front office) e chiedi al cliente se ha ulteriori dettagli
risultato_front_office = agente_front_office.run({"dati_cliente": dati_cliente})
print("Risposta dell'agente di front office:", risultato_front_office)
aggiunta_cliente = input("Hai qualche informazione aggiuntiva o commento da fornire all'agente? ")

# Aggiorna i dati con l'aggiunta del cliente
dati_cliente += f", Informazioni aggiuntive dal cliente: {aggiunta_cliente}"

# Definisci il prompt per l'agente di valutazione delle esigenze
prompt_valutazione = PromptTemplate(
    input_variables=["dati_cliente"],
    template="Analizza i seguenti dati del cliente e suggerisci le coperture assicurative più appropriate: {dati_cliente}"
)
agente_valutazione = LLMChain(llm=llm, prompt=prompt_valutazione)

# Esegui il secondo agente (valutazione delle esigenze) e chiedi ulteriori dettagli al cliente
risultato_valutazione = agente_valutazione.run({"dati_cliente": dati_cliente})
print("Risposta dell'agente di valutazione:", risultato_valutazione)
aggiunta_cliente = input("Hai qualche informazione aggiuntiva o commento per l'agente di valutazione? ")

# Aggiorna i dati con le ulteriori informazioni
dati_cliente += f", Ulteriori dettagli del cliente: {aggiunta_cliente}"

# Definisci il prompt per l'agente di generazione del preventivo
prompt_preventivo = PromptTemplate(
    input_variables=["dati_cliente"],
    template="Genera un preventivo dettagliato per le seguenti coperture assicurative: {dati_cliente}"
)
agente_preventivo = LLMChain(llm=llm, prompt=prompt_preventivo)

# Esegui il terzo agente (generazione del preventivo) con l'interazione finale del cliente
risultato_preventivo = agente_preventivo.run({"dati_cliente": dati_cliente})
print("Risultato finale del preventivo:", risultato_preventivo)

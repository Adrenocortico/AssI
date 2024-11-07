import os
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate

# Inizializza il modello GPT-4o-mini
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Interazione iniziale con il cliente
print("Benvenuto in Assistudio Vigevano! Inserisci i dati richiesti per poterti mettere in contatto con il nostro agente virtuale.")
nome = input("Inserisci il tuo nome e cognome: ")
età = input("Inserisci la tua età: ")
cliente = input("Sei già cliente di Assistudio Vigevano? (sì/no): ")

# Se il cliente non è censito, raccogli ulteriori dettagli
if cliente.lower() == "no":
    # Richiedi i dettagli aggiuntivi al cliente e salva i dati separatamente
    print("{nome} non risulti essere censito. Procediamo con la raccolta delle informazioni necessarie: indirizzo di residenza, numero di telefono, email e occupazione\n")
    indirizzo = input("Inserisci il tuo indirizzo di residenza: ")
    telefono = input("Inserisci il tuo numero di telefono: ")
    email = input("Inserisci la tua email: ")
    occupazione = input("Inserisci la tua occupazione: ")

    # Indica che il cliente è stato censito
    cliente = "sì"  # Ora trattiamo il cliente come censito

# Se il cliente è censito, procedi con la richiesta del servizio assicurativo
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

# Agente di front office per indirizzare il cliente
prompt_front_office = PromptTemplate(
    input_variables=["nome", "età", "cliente",
                     "tipo_servizio", "identificativo"],
    template=(
        "Sei il front office di un ufficio di assicurazioni che si chiama Assistudio Vigevano. "
        "Un cliente ha fornito i seguenti dettagli:\n"
        "Nome: {nome}\n"
        "Età: {età}\n"
        "Cliente esistente: {cliente}\n"
        "Tipo di servizio: {tipo_servizio}\n"
        "Identificativo: {identificativo}\n"
        "Indirizza il cliente alla sede in Corso Pavia, 71/5 a Vigevano o digli di chiamare il 038174441 se qualcosa va storto in questa richiesta."
    )
)
agente_front_office = prompt_front_office | llm
risultato_front_office = agente_front_office.invoke({
    "nome": nome, "età": età, "cliente": cliente, "tipo_servizio": tipo_servizio, "identificativo": identificativo
})
print("Risposta dell'agente di front office:", risultato_front_office.content)

# Agente di valutazione delle esigenze
prompt_valutazione = PromptTemplate(
    input_variables=["nome", "tipo_servizio"],
    template="Analizza il tipo di servizio richiesto ({tipo_servizio}) per il cliente {nome} e suggerisci le coperture assicurative più appropriate."
)
agente_valutazione = prompt_valutazione | llm
risultato_valutazione = agente_valutazione.invoke(
    {"nome": nome, "tipo_servizio": tipo_servizio})
print("Risposta dell'agente di valutazione:", risultato_valutazione.content)
aggiunta_cliente = input(
    "Hai qualche informazione aggiuntiva o commento per l'agente di valutazione? ")

# Agente di generazione del preventivo
prompt_preventivo = PromptTemplate(
    input_variables=["nome", "tipo_servizio", "aggiunta_cliente"],
    template="Genera un preventivo dettagliato per il cliente {nome} in base al servizio richiesto ({tipo_servizio}). "
             "Dettagli aggiuntivi dal cliente: {aggiunta_cliente}."
)
agente_preventivo = prompt_preventivo | llm
risultato_preventivo = agente_preventivo.invoke({
    "nome": nome, "tipo_servizio": tipo_servizio, "aggiunta_cliente": aggiunta_cliente
})
print("Risultato finale del preventivo:", risultato_preventivo.content)

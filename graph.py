import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langgraph import LangGraph, Node

# Inizializza il modello GPT-4o-mini
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Definizione degli agenti


def assistente_auto(request):
    return f"Raccolgo i dati per un preventivo auto. Dettagli: {request}"


def assistente_infortuni(request):
    return f"Raccolgo i dati per un preventivo infortuni. Dettagli: {request}"


def assistente_salute(request):
    return f"Raccolgo i dati per un preventivo salute. Dettagli: {request}"


def assistente_sinistri(request):
    return f"Gestisco la richiesta di sinistri. Dettagli: {request}"

# Funzione di instradamento del grafico per decidere l'assistente


def instrada_richiesta(request):
    if "auto" in request:
        return "assistente_auto"
    elif "infortuni" in request:
        return "assistente_infortuni"
    elif "salute" in request:
        return "assistente_salute"
    elif "sinistri" in request:
        return "assistente_sinistri"
    else:
        return "assistente_generico"


# Creazione del grafo e aggiunta dei nodi
grafico = LangGraph()

grafico.add_node(Node("instradamento", func=instrada_richiesta))
grafico.add_node(Node("assistente_auto", func=assistente_auto))
grafico.add_node(Node("assistente_infortuni", func=assistente_infortuni))
grafico.add_node(Node("assistente_salute", func=assistente_salute))
grafico.add_node(Node("assistente_sinistri", func=assistente_sinistri))

# Aggiunta degli archi per dirigere le richieste verso gli agenti
grafico.add_edge("instradamento", "assistente_auto",
                 condition=lambda x: x == "assistente_auto")
grafico.add_edge("instradamento", "assistente_infortuni",
                 condition=lambda x: x == "assistente_infortuni")
grafico.add_edge("instradamento", "assistente_salute",
                 condition=lambda x: x == "assistente_salute")
grafico.add_edge("instradamento", "assistente_sinistri",
                 condition=lambda x: x == "assistente_sinistri")

# Richiesta iniziale del cliente
request = "Vorrei informazioni su una polizza auto con garanzie opzionali."

# Esecuzione del grafo a partire dal nodo di instradamento
response = grafico.run("instradamento", request=request)
print("Risposta:", response)

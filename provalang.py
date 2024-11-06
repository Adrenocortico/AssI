import os
from langchain_openai import ChatOpenAI
from langchain import LLMChain, PromptTemplate
from langchain.chains import SimpleSequentialChain

# Inizializza il modello GPT-4o-mini
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Definisci il prompt per l'agente di raccolta dati
prompt_raccolta = PromptTemplate(
    input_variables=["input"],
    template="Sei un assistente che raccoglie informazioni per un preventivo assicurativo. Fai le seguenti domande al cliente: {input}"
)
agente_raccolta = LLMChain(llm=llm, prompt=prompt_raccolta)

# Definisci il prompt per l'agente di valutazione delle esigenze
prompt_valutazione = PromptTemplate(
    input_variables=["dati_cliente"],
    template="Analizza i seguenti dati del cliente e suggerisci le coperture assicurative più appropriate: {dati_cliente}"
)
agente_valutazione = LLMChain(llm=llm, prompt=prompt_valutazione)

# Definisci il prompt per l'agente di generazione del preventivo
prompt_preventivo = PromptTemplate(
    input_variables=["coperture"],
    template="Genera un preventivo dettagliato per le seguenti coperture assicurative: {coperture}"
)
agente_preventivo = LLMChain(llm=llm, prompt=prompt_preventivo)

# Crea la catena sequenziale degli agenti
catena = SimpleSequentialChain(chains=[agente_raccolta, agente_valutazione, agente_preventivo], verbose=True)

# Esegui la catena con l'input iniziale
input_iniziale = "Tipo di assicurazione: auto, casa, infortuni o salute."
risultato = catena.run(input_iniziale)

print(risultato)

import os
import autogen
from autogen import GroupChat, GroupChatManager, UserProxyAgent, AssistantAgent, ConversableAgent

# Configurazione LLM per gli agenti
llm_config = {
    "config_list": [
        {"model": "gpt-4o-mini",
        "api_key": os.environ["OPENAI_API_KEY"]
        }
    ]
}

# Agente Front Office
front_office_agent = autogen.UserProxyAgent(
    name="FrontOfficeAgent",
    system_message="Accoglie il cliente e chiede il tipo di preventivo (casa, auto, infortuni) necessario.",
    code_execution_config={"last_n_messages": 2, "use_docker": False},
    human_input_mode="TERMINATE"
)

# Agente Anagrafico
anagrafico_agent = autogen.AssistantAgent(
    name="AnagraficoAgent",
    system_message="Chiede i dati anagrafici del cliente (nome, cognome, data di nascita, ecc.).",
    llm_config=llm_config,
    code_execution_config={"use_docker": False}
)

# Agente Casa
casa_agent = autogen.AssistantAgent(
    name="CasaAgent",
    system_message="Gestisce i preventivi casa. Chiede dettagli specifici come indirizzo e tipo di casa.",
    llm_config=llm_config,
    code_execution_config={"use_docker": False}
)

# Agente Auto
auto_agent = autogen.AssistantAgent(
    name="AutoAgent",
    system_message="Gestisce i preventivi auto. Chiede dettagli specifici come marca, modello, anno dell'auto.",
    llm_config=llm_config,
    code_execution_config={"use_docker": False}
)

# Agente Infortuni
infortuni_agent = autogen.AssistantAgent(
    name="InfortuniAgent",
    system_message="Gestisce i preventivi infortuni. Chiede dettagli specifici come tipo di copertura e rischi associati.",
    llm_config=llm_config,
    code_execution_config={"use_docker": False}
)

# Agente Riassuntivo
riassuntivo_agent = autogen.AssistantAgent(
    name="RiassuntivoAgent",
    system_message="Fornisce un riassunto dei dati anagrafici e del preventivo scelto per la conferma finale.",
    llm_config=llm_config,
    code_execution_config={"use_docker": False}
)

# Creazione dei Gruppi di Chat
# Gruppo principale che guida l'interazione iniziale e di smistamento
groupchat_front_office = autogen.GroupChat(
    agents=[front_office_agent, anagrafico_agent],
    messages=[],
    max_round=3
)

# Gruppi per ciascun tipo di preventivo
groupchat_casa = autogen.GroupChat(
    agents=[casa_agent],
    messages=[],
    max_round=3
)

groupchat_auto = autogen.GroupChat(
    agents=[auto_agent],
    messages=[],
    max_round=3
)

groupchat_infortuni = autogen.GroupChat(
    agents=[infortuni_agent],
    messages=[],
    max_round=3
)

# Gruppo finale per il riassunto
groupchat_riassuntivo = autogen.GroupChat(
    agents=[riassuntivo_agent],
    messages=[],
    max_round=1
)

# Gestione del flusso di chat


class AssicurativoFlowManager:
    def __init__(self):
        # Creazione dei gruppi di chat per ogni fase
        self.groupchat_front_office = groupchat_front_office
        self.groupchat_casa = groupchat_casa
        self.groupchat_auto = groupchat_auto
        self.groupchat_infortuni = groupchat_infortuni
        self.groupchat_riassuntivo = groupchat_riassuntivo

    def start_groupchat(self, groupchat):
        for _ in range(groupchat.max_round):
            # Simuliamo la conversazione tra gli agenti nel gruppo
            for agent in groupchat.agents:
                # Ogni agente risponde ai messaggi
                response = agent.respond(groupchat.messages)
                groupchat.messages.append(response)
                print(f"{agent.name}: {response.content}")

    def start_flow(self):
        # Inizia la conversazione con il front office
        print("Inizio della conversazione con il front office...")
        self.start_groupchat(self.groupchat_front_office)

        # Determina il tipo di preventivo dall'ultimo messaggio
        tipo_preventivo = self.groupchat_front_office.messages[-1].content
        if "casa" in tipo_preventivo.lower():
            print("Indirizzamento al gruppo Casa.")
            self.start_groupchat(self.groupchat_casa)
        elif "auto" in tipo_preventivo.lower():
            print("Indirizzamento al gruppo Auto.")
            self.start_groupchat(self.groupchat_auto)
        elif "infortuni" in tipo_preventivo.lower():
            print("Indirizzamento al gruppo Infortuni.")
            self.start_groupchat(self.groupchat_infortuni)

        # Mostra il riassunto finale
        print("Mostra il riassunto dei dati raccolti...")
        self.start_groupchat(self.groupchat_riassuntivo)


# Inizializzazione e avvio del flusso assicurativo
flow_manager = AssicurativoFlowManager()
flow_manager.start_flow()

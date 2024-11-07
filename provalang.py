
import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# Carica l'elenco dei comuni italiani
with open('comuni_italiani.txt', 'r') as file:
    comuni_italiani = {line.strip().upper() for line in file.readlines()}

# Funzione di validazione del codice fiscale
def valida_codice_fiscale(cf):
    cf = cf.upper()
    # Verifica della lunghezza
    if len(cf) != 16:
        return False, "Errore: Il codice fiscale deve contenere esattamente 16 caratteri."
    # Verifica del formato
    if not re.match(r'^[A-Z]{6}[0-9]{2}[A-EHLMPR-T][0-9]{2}[A-Z][0-9]{3}[A-Z]$', cf):
        return False, "Errore: Il formato del codice fiscale non è corretto."
    # Calcolo del carattere di controllo
    odd_values = {'0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
                  'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
                  'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
                  'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23}
    even_values = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                   'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
                   'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
                   'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25}
    check_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    total = sum(odd_values[cf[i]] if i %
                2 == 0 else even_values[cf[i]] for i in range(15))
    expected_check_char = check_chars[total % 26]
    if cf[-1] != expected_check_char:
        return False, f"Errore: Il carattere di controllo finale è errato. Dovrebbe essere '{expected_check_char}'."
    return True, "Il codice fiscale è valido."

# Funzione di validazione dell'indirizzo
def valida_indirizzo(indirizzo):
    match = re.match(r"^[A-Za-z\s]+,\s*\d+,\s*([A-Za-z\s]+)$", indirizzo)
    if not match:
        return False
    comune = match.group(1).strip().upper()
    return comune in comuni_italiani

# Funzione di validazione dell'email
def valida_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

# Funzione di validazione del numero di telefono (solo cifre)
def valida_telefono(telefono):
    telefono = telefono.strip()
    return telefono.isdigit() and 9 <= len(telefono) <= 15 and telefono.startswith("3") and len(set(telefono)) > 1


# Inizializza il modello GPT-4o-mini
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Definisci gli assistenti per ogni servizio specifico
def assistente_auto():
    print("Benvenuto all'assistente specializzato per le polizze auto.")
    # Codice specifico per assistenza auto
    # Es. Raccolta dettagli del veicolo, tipo di copertura richiesta, ecc.

def assistente_infortuni():
    print("Benvenuto all'assistente specializzato per le polizze infortuni.")
    # Codice specifico per assistenza infortuni
    # Es. Raccolta dettagli sulla copertura infortuni, beneficiari, ecc.

def assistente_casa():
    print("Benvenuto all'assistente specializzato per le polizze casa.")
    # Codice specifico per assistenza casa
    # Es. Raccolta dettagli sull’immobile, copertura desiderata, ecc.

def assistente_salute():
    print("Benvenuto all'assistente specializzato per le polizze salute.")
    # Codice specifico per assistenza salute
    # Es. Raccolta dettagli su condizioni mediche, copertura sanitaria desiderata, ecc.

def assistente_sinistri():
    print("Benvenuto all'assistente specializzato per la gestione dei sinistri.")
    # Codice specifico per assistenza sinistri
    # Es. Raccolta dettagli sull'incidente, danni, ecc.

# Interazione iniziale con il cliente
print("Benvenuto in Assistudio Vigevano! Inserisci i dati richiesti per poterti mettere in contatto con il nostro agente virtuale.")
nome = input("Inserisci il tuo nome e cognome: ")
cliente = input(
    "Sei già cliente di Assistudio Vigevano? (sì/no): ").strip().lower()

# Normalizza le risposte per "sì" e "no"
if cliente in ["si", "sì", "yes", "s", "y"]:
    cliente = "sì"
elif cliente in ["no", "n", "not"]:
    cliente = "no"

# Gestione del cliente esistente o nuovo
if cliente == "no":
    print(f"{nome} non risulti essere censito. Procediamo con la raccolta delle informazioni necessarie: indirizzo di residenza, numero di telefono, email e occupazione.")
    # Raccolta dei dati anagrafici
    while True:
        indirizzo = input(
            "Inserisci il tuo indirizzo completo di residenza (Via, Numero civico, Città): ")
        if valida_indirizzo(indirizzo):
            break
        else:
            print("Errore: L'indirizzo deve essere nel formato 'Via, Numero civico, Città' e la città deve essere italiana.")
    while True:
        telefono = input("Inserisci il tuo numero di telefono: ")
        if valida_telefono(telefono):
            break
        else:
            print("Errore: Il numero di telefono deve contenere solo cifre, essere lungo tra 9 e 15 cifre, e non contenere cifre tutte uguali.")
    while True:
        email = input("Inserisci la tua email: ")
        if valida_email(email):
            break
        else:
            print(
                "Errore: L'email inserita non è valida. Assicurati che sia nel formato 'esempio@dominio.com'.")
    occupazione = input("Inserisci la tua occupazione: ")
    print("Grazie per aver fornito le informazioni. Ora ti colleghiamo con il nostro front office per ulteriori dettagli.")
    cliente = "sì"  # Ora trattiamo il cliente come censito

# Prompt per interpretare la richiesta del cliente e determinare l'assistente corretto
prompt_instradamento = PromptTemplate(
    input_variables=["richiesta_cliente"],
    template=(
        "Sei un assistente virtuale per un'agenzia assicurativa chiamata Assistudio Vigevano. "
        "Un cliente ti ha fatto la seguente richiesta: '{richiesta_cliente}'. "
        "Determina quale assistente specifico deve rispondere alla richiesta. Le possibili opzioni sono:\n"
        "- 'auto' per richieste su polizze auto\n"
        "- 'casa' per richieste su polizze casa\n"
        "- 'infortuni' per richieste su polizze infortuni\n"
        "- 'salute' per richieste su polizze salute\n"
        "- 'sinistri' per richieste di gestione o denuncia sinistri\n"
        "- 'generico' per domande generiche su assicurazioni o sull'agenzia\n\n"
        "Rispondi semplicemente con l'opzione corretta: 'auto', 'casa', 'infortuni', 'salute', 'sinistri' o 'generico'."
    )
)
instradamento_chain = prompt_instradamento | llm

# Prompt per rispondere a domande generiche con contesto aggiuntivo
prompt_benvenuto = PromptTemplate(
    input_variables=["domanda_cliente"],
    template=(
        "Sei l'assistente front-office di benvenuto di Assistudio Vigevano. Il cliente è già censito e stai per accoglierlo. "
        "Informazioni su Assistudio Vigevano:\n"
        "- Indirizzo: Corso Pavia, 71/5 - Vigevano (PV)\n"
        "- Email: assistudiovigevano@gmail.com\n"
        "- Numero centralino: 038174441\n"
        "- Sito internet: www.assistudiovigevano.com\n\n"
        "Assistudio Vigevano offre una gamma di polizze assicurative per proteggere i suoi clienti in ogni ambito della loro vita:\n"
        "- Polizze auto: copertura per incidenti, furto, incendio, e assistenza stradale.\n"
        "- Polizze casa: protezione contro furto, danni, incendio e calamità naturali.\n"
        "- Polizze infortuni: copertura per infortuni personali, anche sul lavoro.\n"
        "- Polizze salute: copertura per spese sanitarie e assistenza medica.\n"
        "- Gestione sinistri: supporto completo per la gestione di incidenti e richieste di risarcimento.\n\n"
        "I valori di Assistudio Vigevano includono l'affidabilità, la trasparenza e l'attenzione al cliente, con un team esperto e dedicato a garantire sicurezza e tranquillità ai propri assicurati.\n\n"
        "Le sedi sono a Vigevano in Corso Pavia, 71/5 e a Cilavegna (PV) in Piazza Garibaldi, 1.\n"
        "Gli orari sono dal lunedì al venerdì dalle 09:00 alle 12:30 e dalle 14:30 alle 19:00, il sabato dalle 10:00 alle 12:00.\n\n"
        "Rispondi alle domande del cliente sulla nostra agenzia o sulle polizze assicurative in generale, "
        "usando queste informazioni per rendere le risposte più complete e rilevanti.\n\n"
        "Domanda del cliente: {domanda_cliente}"
    )
)
assistente_benvenuto_chain = prompt_benvenuto | llm

prompt_saluto = PromptTemplate(
    input_variables=["nome_cliente"],
    template=(
        "Stai concludendo una conversazione con un cliente di nome {nome_cliente} per Assistudio Vigevano. "
        "Salute in modo amichevole e professionale per chiudere la conversazione in modo positivo. Scrivi un messaggio unico e cordiale."
        "Includi un augurio e invita il cliente a contattare di nuovo l'agenzia se ha altre domande."
        "Non firmarti mai."
    )
)
saluto_chain = prompt_saluto | llm

# Funzione dell'assistente di benvenuto per i clienti già censiti
def assistente_benvenuto_cliente():
    print("Benvenuto da Assistudio Vigevano! Sono qui per assisterti con le tue esigenze assicurative.")
    print("Ecco alcune informazioni di base su di noi:")
    print("Indirizzo: Corso Pavia, 71/5 – 27029 – Vigevano (PV)")
    print("Email: assistudiovigevano@gmail.com")
    print("Numero centralino: 038174441")
    print("Sono qui per aiutarti! Dimmi pure come posso assisterti.")

    while True:
        richiesta = input(
            "Hai qualche domanda o richiesta specifica? (Digita 'fine' per uscire): ").strip().lower()

        if richiesta == "fine":
            # Usa LangChain per generare un saluto finale unico e vario
            saluto_finale = saluto_chain.invoke({"nome_cliente": nome})
            # Mostra il saluto finale una sola volta
            print(saluto_finale.content)
            return  # Esce immediatamente senza chiedere ulteriori informazioni
        else:
            # Usa LangChain per interpretare la richiesta e decidere l'assistente corretto
            risposta = instradamento_chain.invoke(
                {"richiesta_cliente": richiesta})
            # Estrai il testo dal dizionario
            decisione = risposta.content.strip().lower()

            # Instrada il cliente all'assistente specifico in base alla decisione
            if decisione == "auto":
                print("Connettendo all'assistente specializzato per auto...")
                assistente_auto()
                return
            elif decisione == "casa":
                print("Connettendo all'assistente specializzato per casa...")
                assistente_casa()
                return
            elif decisione == "infortuni":
                print("Connettendo all'assistente specializzato per infortuni...")
                assistente_infortuni()
                return
            elif decisione == "salute":
                print("Connettendo all'assistente specializzato per salute...")
                assistente_salute()
                return
            elif decisione == "sinistri":
                print("Connettendo all'assistente specializzato per sinistri...")
                assistente_sinistri()
                return
            elif decisione == "generico":
                # Rispondi alle domande generiche tramite LangChain
                risposta_generica = assistente_benvenuto_chain.invoke(
                    {"domanda_cliente": richiesta})
                print("Risposta dell'assistente:", risposta_generica.content)
            else:
                print(
                    "Non sono riuscito a determinare l'assistenza corretta. Riprova con maggiori dettagli.")


# Flusso principale
if cliente == "sì":
    assistente_benvenuto_cliente()
else:
    # Codice per i nuovi clienti (già incluso nel tuo script attuale)
    pass

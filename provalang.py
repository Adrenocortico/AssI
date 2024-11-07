import os
import re
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate

# Carica l'elenco dei comuni italiani
with open('comuni_italiani.txt', 'r') as file:
    comuni_italiani = {line.strip().upper() for line in file.readlines()}

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
    return (
        telefono.isdigit() and
        9 <= len(telefono) <= 15 and
        telefono.startswith("3") and
        len(set(telefono)) > 1  # Evita numeri con tutte le cifre uguali
    )

# Funzione di validazione del codice fiscale con feedback dettagliato


def valida_codice_fiscale(cf):
    cf = cf.upper()

    # Verifica della lunghezza
    if len(cf) != 16:
        return False, "Errore: Il codice fiscale deve contenere esattamente 16 caratteri."

    # Verifica del formato (6 lettere, 2 numeri, 1 lettera, 2 numeri, 1 lettera, 3 numeri, 1 lettera)
    if not re.match(r'^[A-Z]{6}[0-9]{2}[A-EHLMPR-T][0-9]{2}[A-Z][0-9]{3}[A-Z]$', cf):
        return False, "Errore: Il formato del codice fiscale non è corretto. Controlla di aver inserito lettere e numeri nelle posizioni giuste."

    # Coefficenti per il calcolo del carattere di controllo
    odd_values = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
        'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
        'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
    }
    even_values = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
        'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
        'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25
    }
    check_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # Calcolo del totale per il checksum
    total = 0
    for i in range(15):
        char = cf[i]
        if i % 2 == 0:  # Caratteri in posizione dispari
            total += odd_values[char]
        else:  # Caratteri in posizione pari
            total += even_values[char]

    # Determina il carattere di controllo atteso
    expected_check_char = check_chars[total % 26]
    if cf[-1] != expected_check_char:
        return False, f"Errore: Il carattere di controllo finale è errato. Dovrebbe essere '{expected_check_char}', ma è '{cf[-1]}'."

    # Se tutte le verifiche passano
    return True, "Il codice fiscale è valido."

# Inizializza il modello GPT-4o-mini
llm = ChatOpenAI(model_name="gpt-4o-mini")

# Interazione iniziale con il cliente
print("Benvenuto in Assistudio Vigevano! Inserisci i dati richiesti per poterti mettere in contatto con il nostro agente virtuale.")
nome = input("Inserisci il tuo nome e cognome: ")
età = input("Inserisci la tua età: ")
cliente = input("Sei già cliente di Assistudio Vigevano? (sì/no): ")

# Se il cliente non è censito, raccogli ulteriori dettagli
if cliente.lower() == "no":
    print(f"{nome} non risulti essere censito. Procediamo con la raccolta delle informazioni necessarie: indirizzo di residenza, numero di telefono, email e occupazione\n")

    # Validazione e raccolta dell'indirizzo
    while True:
        indirizzo = input(
            "Inserisci il tuo indirizzo completo di residenza (Via, Numero civico, Città): ")
        if valida_indirizzo(indirizzo):
            break
        else:
            print("Errore: L'indirizzo deve essere nel formato 'Via, Numero civico, Città' e la città deve essere italiana.")

    # Validazione e raccolta del numero di telefono
    while True:
        telefono = input("Inserisci il tuo numero di telefono: ")
        if valida_telefono(telefono):
            break
        else:
            print("Errore: Il numero di telefono deve contenere solo cifre, essere lungo tra 9 e 15 cifre, e non contenere cifre tutte uguali.")

    # Validazione e raccolta dell'email
    while True:
        email = input("Inserisci la tua email: ")
        if valida_email(email):
            break
        else:
            print(
                "Errore: L'email inserita non è valida. Assicurati che sia nel formato 'esempio@dominio.com'.")

    # Raccolta dell'occupazione (nessun controllo specifico)
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
        "- Informazioni aggiuntive\n"
        "Risposta: "
    )

    # Validazione e raccolta del codice fiscale con feedback dettagliato
    while True:
        identificativo = input("Per procedere, indica il tuo codice fiscale: ")
        is_valid, message = valida_codice_fiscale(identificativo)
        print(message)
        if is_valid:
            break


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

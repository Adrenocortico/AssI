import os
import re
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate

# Carica l'elenco dei comuni italiani
with open('comuni_italiani.txt', 'r') as file:
    comuni_italiani = {line.strip().upper() for line in file.readlines()}

# Funzione di validazione del codice fiscale
def calcola_carattere_di_controllo(cf_parziale):
    # Coefficienti per il calcolo del carattere di controllo
    valori_pari = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
        'K': 0, 'L': 1, 'M': 2, 'N': 3, 'O': 4, 'P': 5, 'Q': 6, 'R': 7, 'S': 8, 'T': 9,
        'U': 0, 'V': 1, 'W': 2, 'X': 3, 'Y': 4, 'Z': 5
    }

    valori_dispari = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
        'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
        'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
    }

    somma = 0
    for i, c in enumerate(cf_parziale):
        if i % 2 == 0:  # posizione dispari
            somma += valori_dispari[c]
        else:           # posizione pari
            somma += valori_pari[c]

    return chr((somma % 26) + ord('A'))


def valida_codice_fiscale(cf):
    # Verifica la lunghezza del codice fiscale
    if len(cf) != 16:
        return False, "La lunghezza del codice fiscale deve essere di 16 caratteri."

    # Controllo formato generale (solo lettere e numeri)
    if not re.match(r'^[A-Z0-9]{16}$', cf):
        return False, "Il codice fiscale deve contenere solo caratteri alfanumerici maiuscoli."

    # Dividi le parti del codice fiscale
    cf_parziale = cf[:15]
    carattere_di_controllo = cf[15]

    # Calcola il carattere di controllo e verifica
    carattere_calcolato = calcola_carattere_di_controllo(cf_parziale)
    if carattere_calcolato != carattere_di_controllo:
        return False, f"Il carattere di controllo non è corretto. Doveva essere '{carattere_calcolato}', ma è '{carattere_di_controllo}'."

    # Controllo sulla struttura di base (per esempio, verifica se la parte della data e del comune sono valide)
    if not re.match(r'^[A-Z]{6}\d{2}[A-EHLMPR-T][0-9]{2}[A-Z0-9]{4}$', cf):
        return False, "La struttura del codice fiscale non è corretta."

    # Se tutti i controlli sono superati
    return True, "Codice fiscale valido."

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

    # Validazione e raccolta del codice fiscale
    while True:
        identificativo = input("Per procedere, indica il tuo codice fiscale: ")
        if valida_codice_fiscale(identificativo):
            break
        else:
            print("Errore: Il codice fiscale inserito non è valido. Assicurati di inserire un codice fiscale italiano corretto.")

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

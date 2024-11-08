
import os
import re
import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# Carica l'elenco dei comuni italiani
with open('comuni_italiani.txt', 'r') as file:
    comuni_italiani = {line.strip().upper() for line in file.readlines()}

# Funzione di validazione del codice fiscale
def verifica_codice_fiscale(cf):
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
    total = sum(odd_values[cf[i]] if i % 2 == 0 else even_values[cf[i]] for i in range(15))
    expected_check_char = check_chars[total % 26]
    
    if cf[-1] != expected_check_char:
        return False, f"Errore: Il carattere di controllo finale è errato. Dovrebbe essere '{expected_check_char}'."
    return True, "Il codice fiscale è valido."

# Funzione per validare e verificare l'esistenza del codice fiscale tramite chiamata API
def valida_codice_fiscale(cf):
    # Validazione del codice fiscale
    is_valid, message = verifica_codice_fiscale(cf)
    
    if not is_valid:
        return False, message  # Restituisce False se la validazione fallisce
    
    # Se il codice fiscale è valido, effettua la chiamata HTTP per verificarne l'esistenza
    url = "https://assistudio.assieasy.com/assieasy/api/anagrafica/get"
    payload = f'CODICEFISCALE={cf}'
    headers = {
        'chiave-hi': 'ASSIEASY',
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3MzEwODU3NTMsImV4cCI6MTg1NzIyOTc1MywiZGF0YSI6eyJpZCI6IjEzIiwiY2hpYXZlX2hpIjoiQVNTSUhJIn19.Znu-CjXdUG-UMiViWqggbNoaod2lbD7E1Iw6VmvTqEw',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)  # Disabilita SSL solo per test
        response.raise_for_status()  # Verifica eventuali errori HTTP
        data = response.json()  # Ritorna il contenuto della risposta JSON

        # Controllo del campo "data" nella risposta API
        if not data.get("data"):
            return False, "Errore: Il campo 'data' è vuoto o non contiene informazioni valide."
        return True, "Il codice fiscale è valido ed è presente nei nostri sistemi."  # Ritorna il contenuto della risposta JSON se il campo "data" è valido
    except requests.exceptions.RequestException as e:
        return False, f"Errore nella chiamata API: {e}"

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

# Prompt per interpretare la richiesta del cliente e identificare sinonimi di rimozione
prompt_rimozione = PromptTemplate(
    input_variables=["richiesta_cliente", "garanzie"],
    template=(
        "Un cliente ha chiesto: '{richiesta_cliente}'. "
        "Verifica se il cliente sta chiedendo di rimuovere una delle seguenti garanzie: {garanzie}. "
        "Rispondi semplicemente con i nomi delle garanzie da rimuovere, se presenti nella richiesta, oppure rispondi 'Nessuna' se non ci sono garanzie da rimuovere."
    )
)
rimozione_chain = LLMChain(llm=llm, prompt=prompt_rimozione)

# Definisci gli assistenti per ogni servizio specifico
# Prompt di raccolta dati per il preventivo auto
# Set delle garanzie riconosciute
garanzie_possibili_auto = {"assistenza", "cristalli", "tutela legale", "incendio", "furto", "atti vandalici", "fenomeni naturali", "infortuni del conducente", "kasko", "collisione"}

# Prompt per interpretare la richiesta di preventivo auto con informazioni aggiuntive
prompt_auto = PromptTemplate(
    input_variables=["richiesta_cliente", "garanzie_attuali"],
    template=(
        "Sei un assistente virtuale di un'agenzia assicurativa specializzato in polizze auto. "
        "Il cliente ha chiesto: '{richiesta_cliente}'. "
        "Finora, le garanzie richieste dal cliente sono: {garanzie_attuali}.\n\n"
        "Interpreta la richiesta utilizzando le seguenti regole:\n"
        "- 'ATR' si riferisce all'attestato di rischio\n"
        "- Se la polizza è trasferita, l'ATR è già disponibile\n"
        "- Se è una polizza nuova, verifica se il cliente ha classe universale (CU) 14 o richiede l'applicazione del decreto Bersani\n"
        "  - In caso di Decreto Bersani, chiedi al cliente di fornire la targa del veicolo di riferimento\n\n"
        "Rispondi in modo naturale e chiedi solo i dettagli aggiuntivi necessari per completare il preventivo."
    )
)
chain_auto = LLMChain(llm=llm, prompt=prompt_auto)

# Funzione per gestire l'interazione per la polizza auto
def assistente_auto():
    print("Benvenuto all'assistente specializzato per le polizze auto.")
    print("Per iniziare, inserisci la targa del veicolo per il preventivo.")

    # Contesto della conversazione per ricordare la situazione assicurativa e garanzie richieste
    contesto = {
        "targa": None,
        "tipo_polizza": None,   # 'nuova' o 'trasferita'
        "atr": None,            # Se ha ATR o meno
        "garanzie": set()
    }

    # Raccoglie la targa immediatamente
    while not contesto["targa"]:
        contesto["targa"] = input(
            "Inserisci la targa del veicolo: ").strip().upper()
        if not re.match(r'^[A-Z]{2}\d{3}[A-Z]{2}$', contesto["targa"]):
            print("Errore: La targa inserita non è valida. Assicurati di inserire una targa nel formato corretto (es. AB123CD).")
            contesto["targa"] = None

    print(f"Targa registrata: {contesto['targa']}")

    while True:
        richiesta_cliente = input(
            "Descrivi la tua richiesta o digita 'fine' per terminare: ").strip().lower()

        # Controllo della presenza dei dati obbligatori per consentire la chiusura
        if richiesta_cliente == "fine":
            if all([contesto["targa"], contesto["tipo_polizza"], contesto["atr"] is not None, contesto["garanzie"]]):
                print("\n*** Riepilogo della richiesta ***")
                print("Targa:", contesto["targa"])
                print("Tipo di polizza:", contesto["tipo_polizza"])
                print("Attestato di rischio (ATR):",
                      "Presente" if contesto["atr"] else "Non presente")
                print("Garanzie scelte:", ", ".join(contesto["garanzie"]))
                print(
                    "Grazie per aver completato la richiesta. Rimaniamo a disposizione!")
                break
            else:
                print("Mancano ancora dei dati essenziali per completare la richiesta. Assicurati di aver fornito il tipo di polizza, se hai ATR e le garanzie desiderate.")
                continue

        # Usa il modello per interpretare la richiesta e rispondere
        garanzie_attuali = ", ".join(
            contesto["garanzie"]) if contesto["garanzie"] else "Nessuna garanzia ancora selezionata"
        risposta_preventivo = chain_auto.invoke({
            "richiesta_cliente": richiesta_cliente,
            "garanzie_attuali": garanzie_attuali
        })
        risposta_testo = risposta_preventivo["text"]

        # Rileva garanzie da rimuovere usando il modello GPT
        risposta_rimozione = rimozione_chain.invoke(
            {"richiesta_cliente": richiesta_cliente, "garanzie": ", ".join(garanzie_possibili_auto)})
        garanzie_da_rimuovere = risposta_rimozione["text"].split(
            ", ") if risposta_rimozione["text"] != "Nessuna" else []

        # Rimuovi le garanzie specificate per rimozione
        for garanzia in garanzie_da_rimuovere:
            if garanzia in contesto["garanzie"]:
                contesto["garanzie"].discard(garanzia)
                print(f"Garanzia '{garanzia}' rimossa.")

        # Aggiorna i dati obbligatori in base alla richiesta
        if "atr" in richiesta_cliente or "attestato di rischio" in richiesta_cliente:
            contesto["atr"] = True
            contesto["tipo_polizza"] = "trasferita"
            print("Tipo di polizza aggiornato: Trasferita con ATR")

        if "nuova" in richiesta_cliente:
            contesto["tipo_polizza"] = "nuova"
            contesto["atr"] = False
            print("Tipo di polizza aggiornato: Nuova")

        # Aggiunge nuove garanzie richieste
        parole_richiesta = set(richiesta_cliente.split())
        garanzie_richieste = {
            g for g in garanzie_possibili_auto if g in parole_richiesta}
        contesto["garanzie"].update(garanzie_richieste)

        # Mostra la risposta dell'assistente e aggiorna il contesto
        print("Risposta dell'assistente auto:", risposta_testo)

        # Mostra solo le garanzie incluse
        print("\nGaranzie già incluse:", ", ".join(contesto["garanzie"]))
        print("Contesto attuale:", contesto)

def assistente_infortuni():
    print("Benvenuto all'assistente specializzato per le polizze infortuni.")
    # Codice specifico per assistenza infortuni
    # Es. Raccolta dettagli sulla copertura infortuni, beneficiari, ecc.

# Lista delle garanzie nell'ordine desiderato
garanzie_possibili_casa = [
    "incendio del fabbricato", "incendio del contenuto", "fenomeno elettrico", 
    "furto del contenuto", "furto dei gioielli e preziosi", "furto in cassaforte", 
    "scippo e rapina", "responsabilità civile della famiglia", 
    "responsabilità civile della proprietà", "ricorso terzi", "tutela legale"
]

# Prompt per interpretare la risposta del cliente su ogni garanzia
prompt_garanzia = PromptTemplate(
    input_variables=["risposta_cliente"],
    template=(
        "Sei un assistente virtuale di un'agenzia assicurativa. "
        "Il cliente ha risposto: '{risposta_cliente}' alla domanda se desidera includere una garanzia. "
        "Interpreta se la risposta implica l'inclusione o l'esclusione della garanzia. "
        "Rispondi solo con 'includere' o 'escludere'."
    )
)
chain_garanzia = LLMChain(llm=llm, prompt=prompt_garanzia)

def riepilogo_contesto(contesto):
    print("\n*** Riepilogo della richiesta ***")
    print("Ubicazione:", contesto["ubicazione"])
    print("Metri quadri:", contesto["metri_quadri"])
    print("Piani del fabbricato:", contesto["piani_fabbricato"])
    print("Tipo di casa:", contesto["tipo_casa"])
    print("Anno di costruzione/ristrutturazione:", contesto["anno_costruzione"])
    print("Garanzie e massimali selezionati:")
    for garanzia, massimale in contesto["garanzie"].items():
        print(f"  - {garanzia}: Massimale {massimale}")
    print("\nSe hai bisogno di ulteriori modifiche o aggiustamenti, fammelo sapere!")

def verifica_condizioni(contesto):
    """ Verifica le condizioni logiche tra le garanzie e i massimali """
    errori = []

    # Condizioni sulle selezioni delle garanzie
    if "fenomeno elettrico" in contesto["garanzie"]:
        if "incendio del fabbricato" not in contesto["garanzie"] and "incendio del contenuto" not in contesto["garanzie"]:
            errori.append("Per includere il fenomeno elettrico è necessario selezionare l'incendio del fabbricato o l'incendio del contenuto.")
    
    if "furto dei gioielli e preziosi" in contesto["garanzie"] or "furto in cassaforte" in contesto["garanzie"] or "scippo e rapina" in contesto["garanzie"]:
        if "furto del contenuto" not in contesto["garanzie"]:
            errori.append("Per includere furto di gioielli, cassaforte o scippo, è necessario selezionare il furto del contenuto.")

    if "responsabilità civile della proprietà" in contesto["garanzie"] and "ricorso terzi" in contesto["garanzie"]:
        errori.append("Non è possibile selezionare contemporaneamente la responsabilità civile della proprietà e il ricorso terzi.")

    # Condizioni sui massimali
    if "incendio del contenuto" in contesto["garanzie"] and "furto del contenuto" in contesto["garanzie"]:
        if contesto["garanzie"]["incendio del contenuto"] < contesto["garanzie"]["furto del contenuto"]:
            errori.append("Il massimale dell'incendio del contenuto non può essere inferiore al massimale del furto del contenuto.")
    
    if "furto dei gioielli e preziosi" in contesto["garanzie"] and contesto["garanzie"]["furto dei gioielli e preziosi"] > contesto["garanzie"]["furto del contenuto"]:
        errori.append("Il massimale per il furto di gioielli e preziosi non può essere maggiore del massimale del furto del contenuto.")
    
    if "furto in cassaforte" in contesto["garanzie"] and contesto["garanzie"]["furto in cassaforte"] > contesto["garanzie"]["furto del contenuto"]:
        errori.append("Il massimale per il furto in cassaforte non può essere maggiore del massimale del furto del contenuto.")

    if "responsabilità civile della famiglia" in contesto["garanzie"] and contesto["garanzie"]["responsabilità civile della famiglia"] < 250000:
        errori.append("Il massimale per la responsabilità civile della famiglia non può essere inferiore a 250000.")

    if "responsabilità civile della proprietà" in contesto["garanzie"] and contesto["garanzie"]["responsabilità civile della proprietà"] < 250000:
        errori.append("Il massimale per la responsabilità civile della proprietà non può essere inferiore a 250000.")

    return errori

def assistente_casa():
    print("Benvenuto all'assistente specializzato per le polizze casa.")
    print("Per iniziare, raccogliamo alcune informazioni di base sull'immobile per il preventivo.")
    
    contesto = {
        "ubicazione": None,
        "metri_quadri": None,
        "piani_fabbricato": None,
        "tipo_casa": None,
        "anno_costruzione": None,
        "garanzie": {}
    }

    # Raccoglie l'ubicazione del rischio immediatamente
    while not contesto["ubicazione"]:
        contesto["ubicazione"] = input("Inserisci l'ubicazione dell’immobile (indirizzo): ").strip()
        if not valida_indirizzo(contesto["ubicazione"]):
            print("Errore: Inserisci un indirizzo valido nel formato 'Via, Numero civico, Città'.")

    # Raccoglie le altre informazioni necessarie per il preventivo
    while not contesto["metri_quadri"]:
        try:
            contesto["metri_quadri"] = int(input("Inserisci i metri quadri dell’immobile: ").strip())
        except ValueError:
            print("Errore: Inserisci un numero valido per i metri quadri.")

    while not contesto["piani_fabbricato"]:
        try:
            contesto["piani_fabbricato"] = int(input("Inserisci il numero di piani del fabbricato: ").strip())
        except ValueError:
            print("Errore: Inserisci un numero valido per i piani.")

    while not contesto["tipo_casa"]:
        contesto["tipo_casa"] = input("Inserisci il tipo di casa (es. appartamento, villa): ").strip().lower()
        if not contesto["tipo_casa"]:
            print("Errore: Il tipo di casa è obbligatorio.")

    while not contesto["anno_costruzione"]:
        try:
            contesto["anno_costruzione"] = int(input("Inserisci l'anno di costruzione o dell'ultima ristrutturazione completa: ").strip())
        except ValueError:
            print("Errore: Inserisci un numero valido per l'anno.")

    print("\nDettagli dell'immobile registrati correttamente.")

    # Selezione delle garanzie con interpretazione della risposta tramite LangChain
    print("\nPer ogni garanzia disponibile, rispondi con un linguaggio naturale se vuoi includerla o meno.")
    
    for garanzia in garanzie_possibili_casa:
        # Controlli per garantire le dipendenze delle garanzie
        if garanzia == "fenomeno elettrico" and ("incendio del fabbricato" not in contesto["garanzie"] and "incendio del contenuto" not in contesto["garanzie"]):
            print("Per includere il fenomeno elettrico è necessario selezionare l'incendio del fabbricato o l'incendio del contenuto.")
            continue
        if garanzia in ["furto dei gioielli e preziosi", "furto in cassaforte", "scippo e rapina"] and "furto del contenuto" not in contesto["garanzie"]:
            print(f"Per includere '{garanzia}' è necessario selezionare il furto del contenuto.")
            continue
        if garanzia == "ricorso terzi" and "responsabilità civile della proprietà" in contesto["garanzie"]:
            print("Non è possibile selezionare ricorso terzi insieme alla responsabilità civile della proprietà.")
            continue

        risposta_cliente = input(f"Vuoi includere la garanzia '{garanzia}'? ").strip().lower()
        decisione = chain_garanzia.invoke({"risposta_cliente": risposta_cliente})["text"].strip().lower()
        if decisione == "includere":
            contesto["garanzie"][garanzia] = None  # Placeholder per il massimale

    # Chiede i massimali per le garanzie selezionate
    for garanzia in list(contesto["garanzie"]):
        if garanzia == "incendio del fabbricato":
            contesto["garanzie"]["incendio del fabbricato"] = int(input("Specifica il massimale per 'incendio del fabbricato': "))
        elif garanzia == "incendio del contenuto":
            contesto["garanzie"]["incendio del contenuto"] = int(input("Specifica il massimale per 'incendio del contenuto': "))
        elif garanzia == "furto del contenuto":
            contesto["garanzie"]["furto del contenuto"] = int(input("Specifica il massimale per 'furto del contenuto': "))
            if "furto dei gioielli e preziosi" in contesto["garanzie"]:
                contesto["garanzie"]["furto dei gioielli e preziosi"] = int(input("Specifica il massimale per 'furto dei gioielli e preziosi': "))
            if "scippo e rapina" in contesto["garanzie"]:
                contesto["garanzie"]["scippo e rapina"] = int(input("Specifica il massimale per 'scippo e rapina': "))
        else:
            contesto["garanzie"][garanzia] = int(input(f"Specifica il massimale per '{garanzia}': "))

    # Verifica delle condizioni logiche e dei massimali
    errori = verifica_condizioni(contesto)
    if errori:
        print("\nSono stati rilevati i seguenti errori:\n- " + "\n- ".join(errori))
        print("Correggi le informazioni e riprova.")
        return

    # Riepilogo finale
    riepilogo_contesto(contesto)

    while True:
        modifica = input("\nDesideri fare modifiche? Se sì, descrivi la modifica, oppure digita 'fine' per terminare: ").strip().lower()
        if modifica == "fine":
            print("Grazie per aver completato la richiesta. Rimaniamo a disposizione!")
            break
        else:
            # Aggiunge nuove garanzie solo se presenti nella lista di garanzie possibili
            if "aggiungi" in modifica:
                garanzia_da_aggiungere = modifica.replace("aggiungi", "").strip()
                if garanzia_da_aggiungere in garanzie_possibili_casa:
                    if garanzia_da_aggiungere not in contesto["garanzie"]:
                        contesto["garanzie"][garanzia_da_aggiungere] = int(input(f"Specifica il massimale per '{garanzia_da_aggiungere}': "))
                        print(f"Garanzia '{garanzia_da_aggiungere}' aggiunta.")
                    else:
                        print(f"La garanzia '{garanzia_da_aggiungere}' è già presente.")
                else:
                    print(f"La garanzia '{garanzia_da_aggiungere}' non è disponibile. Ecco l'elenco delle garanzie disponibili: {', '.join(garanzie_possibili_casa)}")

            # Usa il modello per interpretare modifiche ad altre parti del contesto
            prompt_modifiche = PromptTemplate(
                input_variables=["modifica", "contesto_attuale"],
                template=(
                    "Sei un assistente assicurativo per una polizza casa. Il cliente ha richiesto la seguente modifica: '{modifica}'. "
                    "Contesto attuale della polizza: {contesto_attuale}. "
                    "Se la modifica riguarda un dato dell'immobile, aggiorna il dato; se riguarda una garanzia, aggiorna o modifica il massimale o rimuovi la garanzia."
                )
            )
            modifiche_chain = LLMChain(llm=llm, prompt=prompt_modifiche)
            risposta_modifica = modifiche_chain.invoke({
                "modifica": modifica,
                "contesto_attuale": contesto
            })
            print("Modifica applicata:", risposta_modifica["text"])
            riepilogo_contesto(contesto)

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
                while True:
                    identificativo = input("Per procedere, indica il tuo codice fiscale: ")
                    is_valid, message = valida_codice_fiscale(identificativo)
                    print(message)
                    if is_valid:
                        break
                assistente_auto()
                return
            elif decisione == "casa":
                print("Connettendo all'assistente specializzato per casa...")
                while True:
                    identificativo = input(
                        "Per procedere, indica il tuo codice fiscale: ")
                    is_valid, message = valida_codice_fiscale(identificativo)
                    print(message)
                    if is_valid:
                        break
                assistente_casa()
                return
            elif decisione == "infortuni":
                print("Connettendo all'assistente specializzato per infortuni...")
                while True:
                    identificativo = input(
                        "Per procedere, indica il tuo codice fiscale: ")
                    is_valid, message = valida_codice_fiscale(identificativo)
                    print(message)
                    if is_valid:
                        break
                assistente_infortuni()
                return
            elif decisione == "salute":
                print("Connettendo all'assistente specializzato per salute...")
                while True:
                    identificativo = input(
                        "Per procedere, indica il tuo codice fiscale: ")
                    is_valid, message = valida_codice_fiscale(identificativo)
                    print(message)
                    if is_valid:
                        break
                assistente_salute()
                return
            elif decisione == "sinistri":
                print("Connettendo all'assistente specializzato per sinistri...")
                while True:
                    identificativo = input(
                        "Per procedere, indica il tuo codice fiscale: ")
                    is_valid, message = valida_codice_fiscale(identificativo)
                    print(message)
                    if is_valid:
                        break
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

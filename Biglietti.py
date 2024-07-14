# Funzione per elencare i concerti con disponibilità di biglietti
# Crea una lista di concerti che hanno ancora biglietti disponibili.
# Utilizza una list comprehension per filtrare i concerti che hanno 
# disponibilità_biglietti maggiore di 0.
def mostra_concerti_disponibili():
    concerti = [concerto for concerto in db['concerti'] if concerto["disponibilità_biglietti"] > 0]
    for concerto in concerti:
        print(f"{concerto['_id']} - {concerto['nome_concerto']} - Disponibilità: {concerto['disponibilità_biglietti']} biglietti")

# Funzione per gestire l'acquisto di biglietti
def acquista_biglietti():
    nome_concerto = input("Inserisci il nome del concerto: ")
    # Cerca nel database un concerto il cui nome corrisponde all'input dell'utente (ignorando maiuscole/minuscole).
    # Utilizza next per ottenere il primo risultato corrispondente, oppure None se non trova nessun concerto.
    concerto = next((concerto for concerto in db['concerti'] if concerto["nome_concerto"].lower() == nome_concerto.lower()), None)
    
    # Verifica se è stato trovato un concerto e se ci sono biglietti disponibili.
    if concerto and concerto['disponibilità_biglietti'] > 0:
        print(f"Prezzo del biglietto: {concerto['prezzo']} EUR")
        # Chiede all'utente quanti biglietti vuole acquistare e converte 
        # l'input in un intero, memorizzandolo in num_biglietti.
        num_biglietti = int(input("Quanti biglietti vuoi acquistare? "))
        
        # Verifica se il numero di biglietti richiesti è maggiore della disponibilità
        if num_biglietti > concerto['disponibilità_biglietti']:
            print("Non ci sono abbastanza biglietti disponibili.")
            return
        
        # Calcola il prezzo totale dei biglietti moltiplicando il prezzo 
        # del biglietto per il numero di biglietti richiesti.
        prezzo_totale = float(concerto['prezzo']) * num_biglietti
        print(f"Prezzo totale per {num_biglietti} biglietti: {prezzo_totale:.2f} EUR")
        
        #Chiede all'utente di confermare l'acquisto
        conferma = input("Confermi l'acquisto? (si/no): ")
        if conferma.lower() != 'si':
            print("Acquisto annullato.")
            return
        
        # Aggiorna la disponibilità dei biglietti
        #diminuendo il numero di biglietti disponibili per il concerto acquistato
        concerto['disponibilità_biglietti'] -= num_biglietti
        
        # Crea un dizionario con i dettagli dell'acquisto, inclusi il nome dell'utente,
        # l'ID del concerto, il nome del concerto, 
        # la quantità di biglietti e il prezzo totale.
        acquisto = {
            "utente": input("Inserisci il tuo nome: "),
            "concerto_id": concerto["_id"],
            "nome_concerto": concerto['nome_concerto'],
            "quantità": num_biglietti,
            "prezzo_totale": prezzo_totale
        }
        # Aggiunge il dizionario dell'acquisto alla collezione biglietti nel database.
        db['biglietti'].append(acquisto)
        
        # Cerca se l'utente ha già effettuato acquisti in precedenza. 
        # Se trova un utente con lo stesso nome, restituisce il record dell'utente,
        # altrimenti None
        utente = next((utente for utente in db['acquisti'] if utente["nome"] == acquisto['utente']), None)
        
        # Verifica se l'utente esiste nel database degli acquisti.
        if utente:
            utente['storico_acquisti'].append(acquisto)
        # Se l'utente non esiste nel database degli acquisti, 
        # crea un nuovo record per l'utente    
        else:
            nuovo_utente = {
                "nome": acquisto['utente'],
                "storico_acquisti": [acquisto]
            }
            db['acquisti'].append(nuovo_utente)
        
        print("Acquisto completato con successo!")
    else:
        print("Concerto non trovato o biglietti esauriti.")

# Esempio di esecuzione
if __name__ == "__main__":
    while True:
        print("\n1. Mostra concerti disponibili")
        print("2. Acquista biglietti")
        print("3. Esci")
        scelta = input("Seleziona un'opzione: ")
        
        if scelta == "1":
            mostra_concerti_disponibili()
        elif scelta == "2":
            acquista_biglietti()
        elif scelta == "3":
            break
        else:
            print("Opzione non valida.")

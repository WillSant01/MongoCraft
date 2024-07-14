from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import os
from datetime import datetime
# Connessione a MongoDB
uri = "mongodb+srv://williamsanteramo:IlPrincipeDiMadrid.10!@cluster0.7x88wem.mongodb.net/?appName=Cluster0"

# Creazione di un nuovo client e connessione al server
client = MongoClient(uri, server_api=ServerApi('1'))

# Invia un ping per confermare la connessione
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Selezione del database e delle collezioni
db = client['ticket_one']
collection_concerti = db['concerti']
collection_biglietti = db['biglietti']
collection_acquisti = db['acquisti']

# Funzione per elencare i concerti con disponibilità di biglietti
def mostra_concerti_disponibili(posti = 0):
    concerti = collection_concerti.find({"disponibilità_biglietti": {"$gt": posti}})
    for concerto in concerti:
        print(f"{concerto['nome_concerto']} - Disponibilità: {concerto['disponibilità_biglietti']} biglietti - Prezzo: {concerto['prezzo']} EUR")

# Funzione per gestire l'acquisto di biglietti
def acquista_biglietti():
    nome_concerto = input("Inserisci il nome del concerto: ")
    concerto = collection_concerti.find_one({"nome_concerto": nome_concerto})
    
    if concerto and concerto['disponibilità_biglietti'] > 0:
        print(f"Prezzo del biglietto: {concerto['prezzo']} EUR")
        
        while True:
            num_biglietti_str = input("Quanti biglietti vuoi acquistare? (digita 'esci' per annullare) ")
            if num_biglietti_str.lower() == 'esci':
                print("Acquisto annullato.")
                return
            
            try:
                num_biglietti = int(num_biglietti_str)
                if num_biglietti > concerto['disponibilità_biglietti']:
                    print("Non ci sono abbastanza biglietti disponibili. Riprova.")
                else:
                    break
            except ValueError:
                print("Per favore, inserisci un numero valido.")
        
        prezzo_totale = concerto['prezzo'] * num_biglietti
        print(f"Prezzo totale per {num_biglietti} biglietti: {prezzo_totale:.2f} EUR")
        
        conferma = input("Confermi l'acquisto? (si/no): ")
        if conferma.lower() != 'si':
            print("Acquisto annullato.")
            return
        
        collection_concerti.update_one(
            {"_id": concerto["_id"]},
            {"$inc": {"disponibilità_biglietti": -num_biglietti}}
        )
        biglietti = {
            "utente": {
                'nome': input("Inserisci il tuo nome: "),
                'mail': input("Inserisci la tua Mail: ")
                },
            "concerto_id": concerto["_id"],
            "quantità": num_biglietti,
            "prezzo_totale": prezzo_totale,
            "data_acquisto": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        collection_biglietti.insert_one(biglietti)
        
        acquisto = {
            "utente": {
                'nome': biglietti["utente"]["nome"],
                'mail': biglietti["utente"]["mail"]
                },
            "storico": [biglietti["_id"]]           
        }
        
        utente = collection_acquisti.find_one({"utente.nome": acquisto['utente']['nome']})
        
        if utente:
            collection_acquisti.update_one(
                {"utente.nome": acquisto['utente']['nome']},  # Filtro per selezionare il documento da aggiornare
                {"$push": {"storico": biglietti["_id"]}}      # Documento di aggiornamento
                )
        else:
            collection_acquisti.insert_one(acquisto)
        
        print("Acquisto completato con successo!")
    else:
        print("Concerto non trovato o biglietti esauriti.")

def mostra_storico(user):
    pipeline = [
        {
            "$match": {
                "utente.nome": user  # Filtro per l'utente specifico
            }
        },
        {
            "$unwind": "$storico"
        },
        {
            "$lookup": {
                "from": "biglietti",
                "localField": "storico",
                "foreignField": "_id",
                "as": "biglietto_info"
            }
        },
        {
            "$unwind": "$biglietto_info"
        },
        {
            "$lookup": {
                "from": "concerti",
                "localField": "biglietto_info.concerto_id",
                "foreignField": "_id",
                "as": "concerto_info"
            }
        },
        {
            "$unwind": "$concerto_info"
        },
        {
            "$project": {
                "_id": 0,
                "utente": "$utente",
                "nome_concerto": "$concerto_info.nome_concerto",
                "artista": "$concerto_info.artista",
                "luogo": "$concerto_info.luogo",
                "data": "$concerto_info.data",
                "prezzo_totale": "$biglietto_info.prezzo_totale",
                "quantità": "$biglietto_info.quantità",
                "data_acquisto": "$biglietto_info.data_acquisto"
            }
        }
    ]
    
   
    result = collection_acquisti.aggregate(pipeline)
    return result

# Esempio di esecuzione
if __name__ == "__main__":
    while True:
        print("\n1. Mostra concerti disponibili")
        print("2. Acquista biglietti")
        print("3. Visualizza acquisti:")
        print("4. Esci")
        scelta = input("Seleziona un'opzione: ")
        
        if scelta == "1":
            mostra_concerti_disponibili()
        elif scelta == "2":
            acquista_biglietti()
        elif scelta == "3": 
            user= input("inserisci il tuo nome: ")
            risultati = mostra_storico(user)
            
            if risultati:
                for doc in risultati:
                    print(json.dumps(doc, indent=4))
                
            
        elif scelta == "4":
            break
        else:
            print("Opzione non valida.")
            
            
            
            
''' print("""
utente: {};
nome_concerto: {};
artista: {};
luogo: {}
data: {}
prezzo_totale: {}
quantità: {}
data_acquisto: {}
""".format(risultati.get('nome_concerto', 'N\A'),
                  risultati.get('artista', {}).get('nome', 'N\A'),
                  risultati.get('artista', {}).get('descrizione', 'N\A')))
            else: 
                print('non hai effettuato acquisti')  '''           
            

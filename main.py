from pymongo import MongoClient
from pymongo.server_api import ServerApi
import geocoder
from geopy.geocoders import Nominatim
from datetime import datetime

uri = "mongodb+srv://williamsanteramo:IlPrincipeDiMadrid.10!@cluster0.7x88wem.mongodb.net/?appName=Cluster0"

# Crea un nuovo client e connettiti al server
client = MongoClient(uri, server_api=ServerApi('1'))

# Invia un ping per confermare una connessione riuscita
try:
    client.admin.command('ping')
    print("Ping al tuo deployment. Connessione a MongoDB avvenuta con successo!")
except Exception as e:
    print(e)

db = client['ticket_one']
collection_concerti = db['concerti']
collection_biglietti = db['biglietti']
collection_utenti = db['utenti']


def ricerca_per_artista(artista):
    concerti = collection_concerti.find({
        '$or': [
            {'artista.nome': {'$regex': artista, '$options': 'i'}},
            {'artista.membri.nome': {'$regex': artista, '$options': 'i'}}
        ]},
        {'_id': 0, 'nome_concerto': 1,
         'artista.tipo': 1, 'artista.nome': 1, 'artista.descrizione': 1, 'artista.membri': 1,
         'luogo.nome': 1, 'data': 1}
    )
    return list(concerti)


def ricerca_per_concerto(concerto):
    concerti = collection_concerti.find({'nome_concerto': {'$regex': concerto, '$options': 'i'}},
                               {'_id': 0, 'artista': 1, 'nome_concerto': 1, 'luogo': 1, 'data': 1})
    return list(concerti)


def mostra_concerto(concerto):
    print("""
Concerto: {};
Artista: {};
Descrizione: {};
Membri:""".format(concerto.get('nome_concerto', 'N\A'),
                  concerto.get('artista', {}).get('nome', 'N\A'),
                  concerto.get('artista', {}).get('descrizione', 'N\A')))

    if concerto.get('artista', {}).get('tipo') == 'band':
        membri = concerto.get('artista', {}).get('membri', [])
        if membri:
            for membro in membri:
                print("- Nome: {} | Strumento: {}".format(membro.get('nome',
                      'N\A'), membro.get('strumento', 'N\A')))
        else:
            print("Nessun membro trovato.")

    print("Luogo: {}".format(concerto.get('luogo', {}).get('nome', 'N\A')))
    print("Data: {}".format(concerto.get('data', 'N\A')))


def converti_input_in_coordinate(input_posizione):
    geolocatore = Nominatim(user_agent="my_app")
    posizione = geolocatore.geocode(input_posizione)

    if posizione:
        return [posizione.longitude, posizione.latitude]
    else:
        raise Exception(
            "Impossibile trovare le coordinate per la posizione inserita")


def concerti_vicini(posizione):
    concerti = collection_concerti.find({
        'luogo.geo': {
            '$near': {
                '$geometry': {
                    'type': "Point",
                    'coordinates': posizione
                },
                '$maxDistance': 7000  # metri
            }}},
        {'_id': 0, 'artista': 1, 'nome_concerto': 1, 'luogo': 1, 'data': 1})

    return list(concerti)


def ricerca_per_intervallo_date(data_inizio, data_fine):
    try:
        # Converti le stringhe di data in oggetti datetime
        data_inizio = datetime.strptime(data_inizio, '%Y-%m-%d')
        data_fine = datetime.strptime(data_fine, '%Y-%m-%d')

        # Pipeline di aggregazione
        pipeline = [
            {
                '$match': {
                    'data': {
                        '$gte': data_inizio,
                        '$lte': data_fine
                    }
                }
            },
            {
                '$sort': {
                    'data': 1
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'artista': 1,
                    'nome_concerto': 1,
                    'luogo': 1,
                    'data': 1
                }
            }
        ]

        concerti = collection_concerti.aggregate(pipeline)

        return list(concerti)

    except Exception as e:
        print(f"Errore durante la ricerca per intervallo di date: {e}")

        return []


def main():
    while True:
        print("\nMenu:")
        print("1| Cerca concerto per artista")
        print("2| Cerca concerto per nome")
        print("3| Trova i concerti a 7 km da te.")
        print("4| Vedi i concerti per intervalli di date.")
        print("5| Entrare nella sezione acquisti")
        print("6| Esci")

        scelta = str(input("\n> Seleziona un'opzione: "))

        match scelta:

            case '1':
                print("\n<<< Inserisci il nome dell'artista: ")
                input_artista = input("\n> ")
                risultati_artista = ricerca_per_artista(input_artista)
                if risultati_artista:
                    for concerto in risultati_artista:
                        mostra_concerto(concerto)
                else:
                    print(
                        "\n<<< Non è stato trovato nessun concerto che corrisponda ai criteri di ricerca")

            case '2':
                print("\n<<< Inserisci il nome del concerto: ")
                input_concerto = input("\n> ")
                risultati_concerto = ricerca_per_concerto(input_concerto)

                if risultati_concerto:
                    for concerto in risultati_concerto:
                        mostra_concerto(concerto)
                else:
                    print(
                        "\n<<< Non è stato trovato nessun concerto che corrisponda ai criteri di ricerca")

            case '3':
                print("\n<<< Vuoi condividere la tua posizione? [y/n]")
                consenso = input("\n> ").lower()

                if consenso == "y":
                    posizione = geocoder.ip('me').latlng[::-1]

                    risultati_distanza = concerti_vicini(posizione)

                    if risultati_distanza:
                        for concerto in risultati_distanza:
                            mostra_concerto(concerto)
                    else:
                        print("\n<<< Non è stato trovato un concerto a 7 km da te.")

                else:
                    print(
                        "\n<<< Inserisci le coordinate manualmente o il nome di una città reale per trovare i concerti nelle vicinanze.")
                    input_posizione = input("\n> ")

                    try:

                        posizione = converti_input_in_coordinate(
                            input_posizione)
                        risultati_distanza = concerti_vicini(posizione)

                        if risultati_distanza:
                            for concerto in risultati_distanza:
                                mostra_concerto(concerto)

                        else:
                            print(
                                "\n<<< Non è stato trovato un concerto nelle vicinanze della posizione inserita.")

                    except Exception as e:
                        print(
                            "\n<<< Errore: Impossibile trovare i concerti. Assicurati di inserire coordinate valide o il nome di una città reale.")

            case '4':
                print("\n<<< Inserisci la data di inizio (YYYY-MM-DD): ")
                data_inizio = input("\n> ")
                print("\n<<< Inserisci la data di fine (YYYY-MM-DD): ")
                data_fine = input("\n> ")

                risultati_intervallo = ricerca_per_intervallo_date(
                    data_inizio, data_fine)

                if risultati_intervallo:
                    for concerto in risultati_intervallo:
                        mostra_concerto(concerto)
                else:
                    print(
                        "\n<<< Non è stato trovato nessun concerto nell'intervallo di date specificato.")
            
            case '5':
                print("\n<<< Inserire il tuo nome prima di continuare:")
                user = input("\n> ").lower()
                main2(user)
                
            case '6':
                print("\n<<< Arrivederci!")
                break

            case _:
                print("\n<<< Opzione non valida. Riprova.")



def mostra_concerti_disponibili(posti = 0):
    
    concerti = collection_concerti.find({"disponibilità_biglietti": {"$gt": posti}})
    for concerto in concerti:
        print(f"""
              
- Concerto: {concerto['nome_concerto']}
- Disponibilità: {concerto['disponibilità_biglietti']} biglietti
- Prezzo: {concerto['prezzo']} EUR""")

    return concerti


def acquista_biglietti(user, risultati):
    
    print("\n<<< Inserire il nome di un concerto:")
    nome_concerto = input("\n> ")
    concerto = None
    
    for result in risultati:
        if result["nome_concerto"] == nome_concerto:
            concerto = result
            break
    
    if concerto:
        print(f"\n<<< Prezzo del biglietto: {concerto['prezzo']} EUR")
        print("<<< Disponibilità: {concerto['disponibilità_biglietti']} biglietti")
        
        while True:
            print("\n<<< Vuoi procedere con l'acquisto? [y\n]")
            scelta = input("\n> ").lower()
            
            if scelta == "y":
                print("\n<<< Quanti biglietti vuoi acquistare? ")
                num_biglietti_str = input("\n> ")
                
                try:
                    num_biglietti = int(num_biglietti_str)
                    if num_biglietti > concerto['disponibilità_biglietti']:
                        print("Non ci sono abbastanza biglietti disponibili. Riprova.")
                    else:
                        break
                    
                except ValueError:
                    print("\n<<< Inserire un numero valido...")
            
                prezzo_totale = concerto['prezzo'] * num_biglietti
                print(f"\n<<< Prezzo totale per {num_biglietti} biglietti: {prezzo_totale:.2f} EUR")
                print("\n<<< Confermi l'acquisto? [y\n]: ")
                conferma = input("\n> ").lower()
                
                if conferma != "y":
                    print("\n<<< Acquisto annullato.")
                    return
                
                collection_concerti.update_one(
                    {"_id": concerto["_id"]},
                    {"$inc": {"disponibilità_biglietti": -num_biglietti}}
                )
                
                biglietti = {
                    "utente": {
                        'nome': user,
                        'mail': str(input("Inserisci la tua Mail: "))
                        },
                    "concerto_id": concerto["_id"],
                    "quantità": num_biglietti,
                    "prezzo_totale": prezzo_totale,
                    "data_acquisto": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                collection_biglietti.insert_one(biglietti)
                
                account = {
                    "utente": {
                        'nome': biglietti["utente"]["nome"],
                        'mail': biglietti["utente"]["mail"]
                        },
                    "storico": [biglietti["_id"]]           
                }
                
                utente = collection_utenti.find_one({"utente.nome": account['utente']['nome']})
                
                if utente:
                    collection_utenti.update_one(
                        {"utente.nome": account['utente']['nome']},  # Filtro per selezionare il documento da aggiornare
                        {"$push": {"storico": biglietti["_id"]}}      # Documento di aggiornamento
                        )
                else:
                    collection_utenti.insert_one(account)
                
                print("Acquisto completato con successo!")
                
            else:
                return
        
    else:
        print("\n<<< Il nome del concerto inserito non è presente tra i disponibili.")
    

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
    
   
    result = collection_utenti.aggregate(pipeline)
    return result


def main2(user):
    while True:
        print(f"\nBenvenuto/a {user.title()}")
        print("1| Mostra concerti disponibili")
        print("2| Acquista biglietti")
        print("3| Visualizza acquisti:")
        print("4| Tornare")
        
        scelta = input("\n> ")
        
        match scelta:
            
            case '1':
                print("\n<<< Inserire il numero minimo dei posti:")
                posti = int(input("\n> "))
                mostra_concerti_disponibili(posti)
            
            case '2':
                risultati = mostra_concerti_disponibili()
                acquista_biglietti(user, risultati)
            
            case '3':
                risultati = mostra_storico(user)
                
                if risultati:
                    
                    print(f"\n Nome utente: {user.title()}")
                    
                    for acquisto in risultati:
                        print(f"Nome concerto: {acquisto['nome_concerto']}")
                        print(f"Artista: {acquisto['artista']}")
                        print(f"Luogo: {acquisto['luogo']}")
                        print(f"Data: {acquisto['data']}")
                        print(f"Prezzo totale: {acquisto['prezzo_totale']}")
                        print(f"Quantità: {acquisto['quantità']}")
                        print(f"Data acquisto: {acquisto['data_acquisto']}")
                
                else:
                    print("\n<<< Non hai ancora effettuato acquisti.")
            
            case '4':
                print("\n<<< Log-out effettuato.")
                break
            
            case _:
                print("\n<<< Scelta non valida...")
                
if __name__ == "__main__":
    main()

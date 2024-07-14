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
collection = db['concerti']

def ricerca_per_artista(artista):
    concerti = collection.find({
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
    concerti = collection.find({'nome_concerto': {'$regex' : concerto, '$options' : 'i'}},
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
                print("- Nome: {} | Strumento: {}".format(membro.get('nome', 'N\A'), membro.get('strumento', 'N\A')))
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
        raise Exception("Impossibile trovare le coordinate per la posizione inserita")

def concerti_vicini(posizione):
    concerti = collection.find({
        'luogo.geo': {
            '$near': {
                '$geometry': {
                    'type': "Point",
                    'coordinates': posizione
                },
                '$maxDistance': 7000 # metri
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
        
        concerti = collection.aggregate(pipeline)
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
        print("4| Vedi concerti per intervallo di date")
        print("5| Esci")

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
                    print("\n<<< Non è stato trovato nessun concerto che corrisponda ai criteri di ricerca")
            
            case '2':
                print("\n<<< Inserisci il nome del concerto: ")
                input_concerto = input("\n> ")
                risultati_concerto = ricerca_per_concerto(input_concerto)

                if risultati_concerto:
                    for concerto in risultati_concerto:
                        mostra_concerto(concerto)
                else:
                    print("\n<<< Non è stato trovato nessun concerto che corrisponda ai criteri di ricerca")
                    
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
                    print("\n<<< Inserisci le coordinate manualmente o il nome di una città reale per trovare i concerti nelle vicinanze.")
                    input_posizione = input("\n> ")
                    
                    try:
                        
                        posizione = converti_input_in_coordinate(input_posizione)
                        risultati_distanza = concerti_vicini(posizione)
        
                        if risultati_distanza:
                            for concerto in risultati_distanza:
                                mostra_concerto(concerto)
                            
                        else:
                            print("\n<<< Non è stato trovato un concerto nelle vicinanze della posizione inserita.")
    
                    except Exception as e:
                        print("\n<<< Errore: Impossibile trovare i concerti. Assicurati di inserire coordinate valide o il nome di una città reale.")
                    
            case '4':
                print("\n<<< Inserisci la data di inizio (YYYY-MM-DD): ")
                data_inizio = input("\n> ")
                print("\n<<< Inserisci la data di fine (YYYY-MM-DD): ")
                data_fine = input("\n> ")
                
                risultati_intervallo = ricerca_per_intervallo_date(data_inizio, data_fine)
                
                if risultati_intervallo:
                    for concerto in risultati_intervallo:
                        mostra_concerto(concerto)
                else:
                    print("\n<<< Non è stato trovato nessun concerto nell'intervallo di date specificato.")
                    
            case '5':
                print("\n<<< Arrivederci!")
                break
            
            case _:
                print("\n<<< Opzione non valida. Riprova.")

if __name__ == "__main__":
    main()
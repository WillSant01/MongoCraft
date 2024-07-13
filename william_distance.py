from pymongo import MongoClient
from pymongo.server_api import ServerApi
import geocoder

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
    
    
def concerti_vicini(posizione):
    pass

def main():
    while True:
        print("\nMenu:")
        print("1| Cerca concerto per artista")
        print("2| Cerca concerto per nome")
        print("3| Trova i concerti a 7 km da te.")
        print("4| Esci")

        scelta = str(input("Seleziona un'opzione: "))
        
        match scelta:
            
            case '1':
                input_artista = input("Inserisci il nome dell'artista: ")
                risultati_artista = ricerca_per_artista(input_artista)
                if risultati_artista:
                    for concerto in risultati_artista:
                        mostra_concerto(concerto)
                else:
                    print("Non è stato trovato nessun concerto che corrisponda ai criteri di ricerca")
            
            case '2':
                input_concerto = input("Inserisci il nome del concerto: ")
                risultati_concerto = ricerca_per_concerto(input_concerto)

                if risultati_concerto:
                    for concerto in risultati_concerto:
                        mostra_concerto(concerto)
                else:
                    print("Non è stato trovato nessun concerto che corrisponda ai criteri di ricerca")
                    
            case '3':
                print("\n<<< Vuoi condividere la tua posizione? ")
                consenso = input("\n> ").lower()
                
                if consenso == "si":
                    posizione = geocoder.ip('me').latlng[::-1]
                    
                    risultati_distanza = concerti_vicini(posizione)
                
                else:
                    print("\n<<< Per trovare concerti vicino a te, devi condividere la tua posizione...")
                    
            case '4':
                print("\nArrivederci!")
                break
            
            case _:
                print("Opzione non valida. Riprova.")


if __name__ == "__main__":
    main()
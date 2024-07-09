from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://williamsanteramo:IlPrincipeDiMadrid.10!@cluster0.7x88wem.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['ticket_one']
collection = db['concerti']

def ricerca_per_artista(artista):
    concerti = collection.find({'artista.nome': artista})
    return list(concerti)


def ricerca_per_concerto(concerto):
    concerti = collection.find({'concerto.nome': concerto})
    return list(concerti)


def main():
    while True:
        print("\nMenu:")
        print("1| Cerca concerto per artista")
        print("2| Cerca concerto per nome")
        print("3| Esci")

        scelta = input("Seleziona un'opzione: ")

        if scelta == '1':
            input_artista = input("Inserisci il nome dell'artista:  ")
            concerti_con_artista = ricerca_per_artista(input_artista)
            for concerto in concerti_con_artista:
                print(concerti_con_artista)

        elif scelta == '2':
            input_concerto = input("Inserisci il nome del concerto: ")
            concerti_con_nome = ricerca_per_concerto(input_concerto)
            for concerto in concerti_con_nome:
                print(concerto)


        elif scelta == '3':
            break

        else:
            print("Opzione non valida. Riprova.")


if __name__ == "__main__":
    main()
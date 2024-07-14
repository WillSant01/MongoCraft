#collezione
{
  "_id": ObjectId("60c72b2f9b1d8b5a4f8f0b6c"),
  "title": "Concerto di esempio",
  "date": ISODate("2024-08-15T19:00:00Z"),
  "location": "Teatro di esempio",
  "price": 50
}


#installazione driver mongodb per Node.js
#npm install mongodb

#codice

const { MongoClient } = require('mongodb');

// URL del database
const url = 'mongodb://localhost:27017';
const dbName = 'concertdb';

async function findConcertsInDateRange(startDate, endDate) {
  const client = new MongoClient(url, { useNewUrlParser: true, useUnifiedTopology: true });

  try {
    await client.connect();
    console.log('Connesso al server MongoDB');

    const db = client.db(dbName);
    const collection = db.collection('concerts');

    // Creazione delle date come oggetti Date
    const start = new Date(startDate);
    const end = new Date(endDate);

    // Query per trovare i concerti nell'intervallo di date
    const concerts = await collection.find({
      date: {
        $gte: start,
        $lte: end
      }
    }).toArray();

    console.log('Concerti trovati:', concerts);
    return concerts;
  } catch (err) {
    console.error(err);
  } finally {
    await client.close();
  }
}

// Intervallo di date specificato
const startDate = '2024-08-01';
const endDate = '2024-08-31';

// Chiamata alla funzione per trovare i concerti
findConcertsInDateRange(startDate, endDate)
  .then(concerts => {
    console.log('Concerti nell\'intervallo di date:', concerts);
  })
  .catch(err => {
    console.error('Errore nella ricerca dei concerti:', err);
  });
  
  
  
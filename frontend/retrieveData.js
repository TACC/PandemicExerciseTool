// retrieveData.js

const { MongoClient } = require('mongodb');

// MongoDB connection URI
const uri = 'mongodb://localhost:27017/';
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

async function retrieveData(day) {
  try {
    await client.connect();
    console.log('Connected to MongoDB');

    const database = client.db('PES');
    const collection = database.collection('days');

    // Convert day to integer (assuming it's passed as an argument or variable)
    const query = { day: parseInt(day) };

    const cursor = collection.find(query);

    await cursor.forEach(doc => {
      console.log(doc); // Print each document retrieved
    });

  } catch (err) {
    console.error('Error retrieving data:', err);
  } finally {
    await client.close();
    console.log('Disconnected from MongoDB');
  }
}

// Assuming day is passed as a command-line argument or variable
const day = parseInt(process.argv[2]); // Convert command-line argument to integer

retrieveData(day);

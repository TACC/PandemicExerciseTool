// testFetchData.js

const { MongoClient } = require('mongodb');
const assert = require('assert');

// Connection URL
const url = 'mongodb://localhost:27017';

// Database Name
const dbName = 'PES';

// Day to query (pass as command-line argument or change here)
const dayToQuery = process.argv[2] ? parseInt(process.argv[2]) : 1; // Default to day 1 if not provided

// Use connect method to connect to the server
MongoClient.connect(url, { useNewUrlParser: true}, async (err, client) => {
  if (err) {
    console.error('Error connecting to MongoDB:', err);
    return;
  }
  console.log('Connected successfully to MongoDB server');

  const db = client.db(dbName);
  const collection = db.collection('days');

  // Find documents based on the day
  try {
    const query = { day: dayToQuery };
    const docs = await collection.find(query).toArray();
    console.log('Found the following records:');
    console.log(docs);
  } catch (error) {
    console.error('Error fetching documents:', error);
  } finally {
    client.close();
  }
});

// server.js

const express = require('express');
const { MongoClient } = require('mongodb');
const assert = require('assert');

const app = express();
const port = 5000;

// Connection URL and Database Name
const url = 'mongodb://localhost:27017';
const dbName = 'PES';

// Use connect method to connect to the server
MongoClient.connect(url, { useUnifiedTopology: true }, (err, client) => {
  assert.strictEqual(null, err);
  console.log('Connected successfully to MongoDB server');
  
  const db = client.db(dbName);
  const collection = db.collection('days');

  // Define endpoint to fetch data by day
  app.get('/data', (req, res) => {
    const day = parseInt(req.query.day); // Assuming day is passed as a query parameter
    collection.find({ day }).toArray((err, docs) => {
      assert.strictEqual(err, null);
      res.json(docs); // Send JSON response back to client
    });
  });

  // Close the MongoDB connection on server close
  app.on('close', () => {
    client.close();
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

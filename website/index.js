require('dotenv').config();

const server = require('./server');

const port = process.env.API_PORT;

server.listen(port, () => {
  console.log(`Telephone API listening on port ${port}`);
});

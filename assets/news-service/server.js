const cds = require('@sap/cds');
const cors = require('cors');
const path = require('path');

cds.on('bootstrap', (app) => {
  app.use(cors());

  const uiPath = path.join(__dirname, 'app', 'dashboard');
  app.use('/app', require('express').static(uiPath));

  app.get('/app/*', (req, res) => {
    res.sendFile(path.join(uiPath, 'index.html'));
  });
});

module.exports = cds.server;

/**
 * Custom CAP server — adds CORS + serves the built React UI under /app
 */
const cds = require('@sap/cds');
const cors = require('cors');
const path = require('path');

cds.on('bootstrap', (app) => {
  // Enable CORS for all routes (dev convenience)
  app.use(cors());

  // Serve the compiled React dashboard at /app/*
  const uiPath = path.join(__dirname, 'app', 'dashboard');
  app.use('/app', require('express').static(uiPath));

  // SPA fallback: send index.html for any /app/* route not matched by a file
  app.get('/app/*', (req, res) => {
    res.sendFile(path.join(uiPath, 'index.html'));
  });
});

module.exports = cds.server;

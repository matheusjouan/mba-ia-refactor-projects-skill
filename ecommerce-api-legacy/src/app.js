const express = require('express');

const config = require('./config');
const database = require('./infra/database');
const errorHandler = require('./middlewares/errorHandler');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');

async function start() {
  const app = express();
  app.use(express.json());

  await database.initSchema();
  await database.seedIfEmpty();

  app.use('/api', checkoutRoutes);
  app.use('/api', reportRoutes);
  app.use('/api', userRoutes);

  app.use(errorHandler);

  app.listen(config.port, () => {
    console.log(`LMS API rodando na porta ${config.port}...`);
  });
}

start();

const db = require('../infra/database');

function findActiveById(id) {
  return db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

function findAll() {
  return db.all('SELECT * FROM courses');
}

module.exports = { findActiveById, findAll };

const db = require('../infra/database');

function findByEmail(email) {
  return db.get('SELECT * FROM users WHERE email = ?', [email]);
}

function findById(id) {
  return db.get('SELECT * FROM users WHERE id = ?', [id]);
}

function create(name, email, passwordHash) {
  return db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
}

function deleteById(id) {
  return db.run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, findById, create, deleteById };

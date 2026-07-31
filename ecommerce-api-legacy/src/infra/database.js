const sqlite3 = require('sqlite3').verbose();

const config = require('../config');
const cryptoService = require('../services/cryptoService');

const db = new sqlite3.Database(config.dbFile);

function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(err) {
      if (err) return reject(err);
      resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) return reject(err);
      resolve(row);
    });
  });
}

function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

async function initSchema() {
  await run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
  await run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
  await run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
  await run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
  await run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
}

async function seedIfEmpty() {
  const row = await get('SELECT COUNT(*) AS count FROM courses');
  if (row.count > 0) return;

  const passwordHash = await cryptoService.hashPassword('123');
  const user = await run(
    'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
    ['Leonan', 'leonan@fullcycle.com.br', passwordHash],
  );
  await run(
    'INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
    ['Clean Architecture', 997.0, 'Docker', 497.0],
  );
  const course = await get('SELECT id FROM courses WHERE title = ?', ['Clean Architecture']);
  const enrollment = await run(
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [user.lastID, course.id],
  );
  await run(
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [enrollment.lastID, 997.0, 'PAID'],
  );
}

module.exports = { run, get, all, initSchema, seedIfEmpty };

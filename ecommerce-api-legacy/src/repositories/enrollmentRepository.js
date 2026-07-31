const db = require('../infra/database');

function create(userId, courseId) {
  return db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
}

function findByCourseId(courseId) {
  return db.all('SELECT * FROM enrollments WHERE course_id = ?', [courseId]);
}

function findByUserId(userId) {
  return db.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
}

function deleteByUserId(userId) {
  return db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
}

module.exports = { create, findByCourseId, findByUserId, deleteByUserId };

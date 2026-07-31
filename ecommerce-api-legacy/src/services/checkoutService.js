const courseRepository = require('../repositories/courseRepository');
const userRepository = require('../repositories/userRepository');
const enrollmentRepository = require('../repositories/enrollmentRepository');
const paymentRepository = require('../repositories/paymentRepository');
const auditLogRepository = require('../repositories/auditLogRepository');
const paymentService = require('./paymentService');
const cryptoService = require('./cryptoService');

class CheckoutError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
  }
}

async function checkout({ name, email, password, courseId, cardNumber }) {
  const course = await courseRepository.findActiveById(courseId);
  if (!course) throw new CheckoutError('Curso não encontrado', 404);

  const existingUser = await userRepository.findByEmail(email);
  let userId;
  if (existingUser) {
    userId = existingUser.id;
  } else {
    const passwordHash = await cryptoService.hashPassword(password || '123456');
    const created = await userRepository.create(name, email, passwordHash);
    userId = created.lastID;
  }

  const status = paymentService.authorize(cardNumber);
  if (status === 'DENIED') throw new CheckoutError('Pagamento recusado', 400);

  const enrollment = await enrollmentRepository.create(userId, courseId);
  await paymentRepository.create(enrollment.lastID, course.price, status);
  await auditLogRepository.record(`Checkout curso ${courseId} por ${userId}`);

  return { enrollmentId: enrollment.lastID, courseTitle: course.title };
}

module.exports = { checkout, CheckoutError };

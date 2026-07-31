const userRepository = require('../repositories/userRepository');
const enrollmentRepository = require('../repositories/enrollmentRepository');
const paymentRepository = require('../repositories/paymentRepository');

async function deleteUserCascade(userId) {
  const enrollments = await enrollmentRepository.findByUserId(userId);
  const enrollmentIds = enrollments.map((enrollment) => enrollment.id);

  await paymentRepository.deleteByEnrollmentIds(enrollmentIds);
  await enrollmentRepository.deleteByUserId(userId);
  await userRepository.deleteById(userId);
}

module.exports = { deleteUserCascade };

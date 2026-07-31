const courseRepository = require('../repositories/courseRepository');
const enrollmentRepository = require('../repositories/enrollmentRepository');
const userRepository = require('../repositories/userRepository');
const paymentRepository = require('../repositories/paymentRepository');

async function generate() {
  const courses = await courseRepository.findAll();

  return Promise.all(courses.map(async (course) => {
    const enrollments = await enrollmentRepository.findByCourseId(course.id);

    const students = await Promise.all(enrollments.map(async (enrollment) => {
      const [user, payment] = await Promise.all([
        userRepository.findById(enrollment.user_id),
        paymentRepository.findByEnrollmentId(enrollment.id),
      ]);
      return {
        student: user ? user.name : 'Unknown',
        paid: payment ? payment.amount : 0,
        paidStatus: payment ? payment.status : null,
      };
    }));

    const revenue = students.reduce(
      (total, student) => total + (student.paidStatus === 'PAID' ? student.paid : 0),
      0,
    );

    return {
      course: course.title,
      revenue,
      students: students.map(({ student, paid }) => ({ student, paid })),
    };
  }));
}

module.exports = { generate };

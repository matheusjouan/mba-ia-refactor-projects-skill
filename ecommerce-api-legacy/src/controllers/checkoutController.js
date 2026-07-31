const checkoutService = require('../services/checkoutService');

async function checkout(req, res, next) {
  try {
    const { usr, eml, pwd, c_id: courseId, card } = req.body;
    if (!usr || !eml || !courseId || !card) {
      return res.status(400).json({ erro: 'Dados obrigatórios ausentes' });
    }

    const result = await checkoutService.checkout({
      name: usr, email: eml, password: pwd, courseId, cardNumber: card,
    });
    res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
  } catch (err) {
    next(err);
  }
}

module.exports = { checkout };

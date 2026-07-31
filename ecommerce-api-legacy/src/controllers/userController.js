const userDeletionService = require('../services/userDeletionService');

async function deleteUser(req, res, next) {
  try {
    await userDeletionService.deleteUserCascade(req.params.id);
    res.json({ mensagem: 'Usuário e dados relacionados (matrículas, pagamentos) removidos com sucesso' });
  } catch (err) {
    next(err);
  }
}

module.exports = { deleteUser };

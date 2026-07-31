const express = require('express');

const reportController = require('../controllers/reportController');

const router = express.Router();
router.get('/admin/financial-report', reportController.financialReport);

module.exports = router;

const financialReportService = require('../services/financialReportService');

async function financialReport(req, res, next) {
  try {
    const report = await financialReportService.generate();
    res.json(report);
  } catch (err) {
    next(err);
  }
}

module.exports = { financialReport };

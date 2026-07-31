module.exports = {
  port: process.env.PORT || 3000,
  dbFile: process.env.DB_FILE || ':memory:',
  dbUser: process.env.DB_USER || 'dev-only-db-user',
  dbPass: process.env.DB_PASS || 'dev-only-db-pass',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'dev-only-payment-key',
  smtpUser: process.env.SMTP_USER || 'dev-only-smtp-user',
};

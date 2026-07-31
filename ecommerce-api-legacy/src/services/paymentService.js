function authorize(cardNumber) {
  return cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
}

module.exports = { authorize };

/**
 * Prevents non-numeric characters (e, E, +, -) in number inputs.
 * Usage: @keydown="blockNonNumeric"
 */
export function blockNonNumeric(event) {
  if (['e', 'E', '+', '-'].includes(event.key)) {
    event.preventDefault();
  }
}

/**
 * Validates Russian phone number format: +7 followed by 10 digits.
 */
export function isValidPhone(phone) {
  return /^\+7\d{10}$/.test(phone);
}

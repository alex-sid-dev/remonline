/**
 * Extracts a human-readable error message from an axios error or generic Error.
 */
export function extractErrorMessage(e, fallback = 'Произошла ошибка') {
  const detail = e?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (typeof e?.message === 'string' && e.message) return e.message;
  return fallback;
}

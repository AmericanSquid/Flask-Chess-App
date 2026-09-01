export function startPoller(callback, intervalMs) {
  const timer = window.setInterval(callback, intervalMs);
  return () => window.clearInterval(timer);
}

/* Optional override: window.__HRMS_API__ = 'https://your-api.example.com'; (omit trailing slash) */
(function () {
  if (typeof window === 'undefined') return;
  if (window.__HRMS_API__) return;
  const loc = window.location;
  const host = loc.hostname;
  const loopback =
    host === 'localhost' || host === '127.0.0.1' || host === '[::1]';
  if (loopback) {
    window.__HRMS_API__ = 'http://127.0.0.1:8787';
  } else if (loc.protocol === 'http:' || loc.protocol === 'https:') {
    window.__HRMS_API__ = loc.origin;
  } else {
    window.__HRMS_API__ = 'http://127.0.0.1:8787';
  }
})();

/* Optional override before any module loads: window.__HRMS_API__ = 'https://your-api.example.com'; */
(function () {
  if (typeof window === 'undefined') return;
  if (!window.__HRMS_API__) window.__HRMS_API__ = 'http://127.0.0.1:8787';
})();

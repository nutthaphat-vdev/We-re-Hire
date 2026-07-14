import indexHtml from './index.html';
import landingHtml from './landing.html';

const CSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' https://maps.googleapis.com https://fonts.googleapis.com https://unpkg.com",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com https://unpkg.com",
  "font-src 'self' https://fonts.gstatic.com https://unpkg.com",
  "img-src 'self' data: blob: https: http:",
  "connect-src 'self' https://we-re-hire.onrender.com https://maps.googleapis.com https://wexupoegrynxbhdzioym.supabase.co",
  "frame-ancestors 'none'",
].join('; ');

const HEADERS = {
  'Content-Type': 'text/html; charset=UTF-8',
  'Cache-Control': 'no-cache, no-store, must-revalidate',
  'Content-Security-Policy': CSP,
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(self), camera=(self), microphone=()',
};

export default {
  async fetch(request) {
    const path = new URL(request.url).pathname;
    // Root + /landing → landing page (Gemini) · ทุก path อื่น → app (index.html SPA)
    // NOTE: OAuth redirect ผูกกับ /index.html → ต้องตกไป indexHtml (app) เสมอ
    const isLanding = (path === '/' || path === '/landing' || path === '/landing.html');
    const body = isLanding ? landingHtml : indexHtml;
    return new Response(body, { headers: HEADERS });
  },
};

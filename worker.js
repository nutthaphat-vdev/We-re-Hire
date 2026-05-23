import html from './index.html';

export default {
  async fetch() {
    return new Response(html, {
      headers: {
        'Content-Type': 'text/html; charset=UTF-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
      },
    });
  },
};

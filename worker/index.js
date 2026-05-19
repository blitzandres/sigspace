export default {
  async fetch(request, env) {
    return new Response('SIGSPACE worker online', { status: 200 });
  }
};

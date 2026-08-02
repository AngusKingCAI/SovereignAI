// Auth module — handles session cookie awareness and logout
// NOTE: No token storage. Auth is entirely session-cookie based.
const Auth = {
  async login(username, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password}),
      credentials: 'same-origin',  // Include session cookie
    });
    if (!res.ok) throw new Error('Login failed');
    return res.json();
  },

  async logout() {
    await fetch('/api/auth/logout', {method: 'POST', credentials: 'same-origin'});
    window.location.href = '/login';
  },

  // No getAuthHeaders() — cookies are sent automatically by the browser
};

// utils/fetchWithAuth.js

/**
 * Custom fetch wrapper to handle authentication
 * @param {string} url - the endpoint to fetch
 * @param {object} options - fetch options
 * @param {string} redirectTo - fallback login URL
 * @returns {Promise} - resolved data or null if unauthorized
 */
async function fetchWithAuth(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            credentials: 'include', // always include cookies/session
        });
        console.log(response.status);
        if (response.status === 401) {
            return;
        }
        return response;

    } catch (error) {
        console.error("Fetch failed:", error);
    }
}


function redirectToLogin() {
    const returnUrl = encodeURIComponent(window.location.href);
    const loginUrl = `/auth/login?next=${returnUrl}&provider=google`;
    window.location.href = loginUrl;
}
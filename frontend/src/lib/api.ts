import axios from 'axios';

// Create an axios instance with a default base URL
// We use an environment variable if available, otherwise fallback to localhost
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
});

// Request interceptor to add the auth token to every request
api.interceptors.request.use(
    (config) => {
        // 1. Get the token from localStorage
        const token = localStorage.getItem("token");

        // 2. If the token exists, add it to the Authorization header
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        // Handle request errors
        return Promise.reject(error);
    }
);

// Response interceptor to handle common errors (like 401 Unauthorized)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Optional: If we receive a 401, we might want to redirect to login
        // or clear the token. expected behavior depends on requirements.
        if (error.response && error.response.status === 401) {
            // console.warn("Unauthorized access - possibly invalid token");
        }
        return Promise.reject(error);
    }
);

export default api;

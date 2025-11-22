/**
 * API Service
 * Handles all API calls to the Django backend
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

/**
 * Fetch portfolio composition from Binance
 * @returns {Promise} Portfolio data
 */
export const getPortfolio = async () => {
    try {
        const response = await api.get('/portfolio/');
        return response.data;
    } catch (error) {
        console.error('Error fetching portfolio:', error);
        throw error;
    }
};

/**
 * Test Binance API connection
 * @returns {Promise} Connection status
 */
export const testConnection = async () => {
    try {
        const response = await api.get('/portfolio/test/');
        return response.data;
    } catch (error) {
        console.error('Error testing connection:', error);
        throw error;
    }
};

export default api;

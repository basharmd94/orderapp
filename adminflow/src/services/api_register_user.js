import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const registerUser = async (userData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/users/registration`, userData);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    let errorMessage = 'Registration failed';
    if (error.response) {
      // Handle specific API error responses
      if (error.response.data.detail) {
        errorMessage = Array.isArray(error.response.data.detail) 
          ? error.response.data.detail.map(err => err.msg).join(', ')
          : error.response.data.detail;
      }
    }
    throw new Error(errorMessage);
  }
};
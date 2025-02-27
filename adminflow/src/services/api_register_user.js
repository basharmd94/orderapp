import axios from 'axios';
import { API_BASE_URL } from '../config';

export const registerUser = async (userData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/admin/users/registration`, userData);
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
import { apiPut } from './api';

export const updateUser = async (userData) => {
  try {
    const response = await apiPut('/admin/user-manage/update-user', userData);
    return {
      success: true,
      data: response
    };
  } catch (error) {
    let errorMessage = 'User update failed';
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

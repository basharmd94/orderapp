import { useState, useEffect } from 'react';
import { Grid, Box, MenuItem } from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import { CustomInput, CustomButton, CustomAutocomplete } from 'ui-component/custom';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import CircularProgress from '@mui/material/CircularProgress';
import SearchIcon from '@mui/icons-material/Search';
import SaveIcon from '@mui/icons-material/Save';
import { apiGet, apiPut } from 'services/api';

const UserUpdate = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [userList, setUserList] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    mobile: '',
    user_id: '',
    status: '',
    businessId: '',
    is_admin: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState({
    search: false,
    submit: false,
    initial: true
  });
  const [alert, setAlert] = useState({
    show: false,
    message: '',
    severity: 'success'
  });

  const businessIdOptions = Array.from({ length: 10 }, (_, i) => ({
    label: `${100000 + i}`,
    value: `${100000 + i}`
  }));

  const statusOptions = [
    { label: 'Active', value: 'active' },
    { label: 'Inactive', value: 'inactive' }
  ];

  const roleOptions = [
    { label: 'Admin', value: 'admin' },
    { label: 'User', value: 'user' }
  ];

  // Fetch all users on component mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(prev => ({ ...prev, initial: true }));
        const response = await apiGet('/admin/user-manage/get-all-users');
        if (Array.isArray(response)) {
          setUserList(response.map(user => ({
            label: `${user.username} (${user.email})`,
            value: user.username,
            ...user
          })));
        }
      } catch (error) {
        console.error('Error fetching users:', error);
        setAlert({
          show: true,
          message: error?.detail || 'Error fetching users',
          severity: 'error'
        });
      } finally {
        setLoading(prev => ({ ...prev, initial: false }));
      }
    };

    fetchUsers();
  }, []);

  // Close alert after 5 seconds
  useEffect(() => {
    let timer;
    if (alert.show) {
      timer = setTimeout(() => {
        setAlert(prev => ({ ...prev, show: false }));
      }, 5000);
    }
    return () => clearTimeout(timer);
  }, [alert.show]);

  const handleSelectUser = (event, newValue) => {
    if (!newValue) {
      setSelectedUser(null);
      setFormData({
        username: '',
        email: '',
        mobile: '',
        user_id: '',
        status: '',
        businessId: '',
        is_admin: '',
        password: ''
      });
      return;
    }

    setSelectedUser(newValue);
    setFormData({
      username: newValue.username,
      email: newValue.email,
      mobile: newValue.mobile || '',
      user_id: newValue.user_id || newValue.employeeCode || '',
      status: newValue.status || 'active',
      businessId: newValue.businessId?.toString() || '',
      is_admin: newValue.is_admin || 'user',
      password: '' // Password is always empty initially
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear errors for this field when it's modified
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    const newErrors = {};
    if (!formData.username) newErrors.username = 'Username is required';
    if (!formData.email) newErrors.email = 'Email is required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(prev => ({ ...prev, submit: true }));
    
    try {
      // Build update data - exclude empty password
      const updateData = { ...formData };
      
      // Only include password if provided
      if (!updateData.password) {
        delete updateData.password;
      }
      
      // Convert businessId to number
      if (updateData.businessId) {
        updateData.businessId = Number(updateData.businessId);
      }

      // Make the API call
      const response = await apiPut('/admin/user-manage/update-user', updateData);
      
      setAlert({
        show: true,
        message: response.message || 'User updated successfully',
        severity: 'success'
      });
      
      // Refresh the user list
      const updatedUsers = await apiGet('/admin/user-manage/get-all-users');
      if (Array.isArray(updatedUsers)) {
        setUserList(updatedUsers.map(user => ({
          label: `${user.username} (${user.email})`,
          value: user.username,
          ...user
        })));
      }
    } catch (error) {
      console.error('Update error:', error);
      setAlert({
        show: true,
        message: error.detail || error.message || 'Error updating user',
        severity: 'error'
      });
    } finally {
      setLoading(prev => ({ ...prev, submit: false }));
    }
  };

  return (
    <MainCard title="Update User">
      {alert.show && (
        <Alert 
          severity={alert.severity}
          sx={{ mb: 2 }}
          onClose={() => setAlert({ ...alert, show: false })}
        >
          <AlertTitle>{alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}</AlertTitle>
          {alert.message}
        </Alert>
      )}

      {loading.initial ? (
        <Box display="flex" justifyContent="center" alignItems="center" height="400px">
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12}>
              <CustomAutocomplete
                options={userList}
                value={selectedUser}
                onChange={handleSelectUser}
                label="Select User"
                placeholder="Search for a user by username or email"
                loading={loading.search}
                fullWidth
              />
            </Grid>
          </Grid>

          {selectedUser && (
            <form onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    label="Username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    error={!!errors.username}
                    helperText={errors.username}
                    InputProps={{
                      readOnly: true,
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    label="Employee ID"
                    name="user_id"
                    value={formData.user_id}
                    onChange={handleChange}
                    error={!!errors.user_id}
                    helperText={errors.user_id}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    type="email"
                    label="Email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    error={!!errors.email}
                    helperText={errors.email}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    label="Mobile"
                    name="mobile"
                    value={formData.mobile}
                    onChange={handleChange}
                    error={!!errors.mobile}
                    helperText={errors.mobile}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    select
                    label="Status"
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    error={!!errors.status}
                    helperText={errors.status}
                  >
                    {statusOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </CustomInput>
                </Grid>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    select
                    label="Business ID"
                    name="businessId"
                    value={formData.businessId}
                    onChange={handleChange}
                    error={!!errors.businessId}
                    helperText={errors.businessId}
                  >
                    {businessIdOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </CustomInput>
                </Grid>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    select
                    label="Role"
                    name="is_admin"
                    value={formData.is_admin}
                    onChange={handleChange}
                    error={!!errors.is_admin}
                    helperText={errors.is_admin}
                  >
                    {roleOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </CustomInput>
                </Grid>
                <Grid item xs={12} md={6}>
                  <CustomInput
                    fullWidth
                    type="password"
                    label="Password (leave empty to keep current)"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    error={!!errors.password}
                    helperText={errors.password}
                  />
                </Grid>
                <Grid item xs={12} sx={{ textAlign: 'right', mt: 2 }}>
                  <CustomButton
                    variant="contained"
                    color="primary"
                    type="submit"
                    disabled={loading.submit}
                    startIcon={loading.submit ? <CircularProgress size={20} /> : <SaveIcon />}
                  >
                    {loading.submit ? 'Updating...' : 'Update User'}
                  </CustomButton>
                </Grid>
              </Grid>
            </form>
          )}
        </>
      )}
    </MainCard>
  );
};

export default UserUpdate;

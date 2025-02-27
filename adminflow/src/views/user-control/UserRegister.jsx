import { useState, useEffect } from 'react';
import { Grid } from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import { CustomInput, CustomButton, CustomAutocomplete } from 'ui-component/custom';
import SendIcon from '@mui/icons-material/Send';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import CheckIcon from '@mui/icons-material/Check';
import { registerUser } from 'services/api_register_user';

const UserRegister = () => {
  const businessIdOptions = Array.from({ length: 10 }, (_, i) => ({
    label: `${100000 + i}`,
    value: `${100000 + i}`
  }));

  const [formData, setFormData] = useState({
    username: '',
    user_id: '',
    email: '',
    mobile: '',
    password: '',
    confirm_password: '',
    businessId: '',
    status: 'active',
    is_admin: '',
    terminal: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', severity: 'success' });

  const validateForm = () => {
    const newErrors = {};
    if (!formData.username) newErrors.username = 'Username is required';
    if (!formData.user_id) newErrors.user_id = 'Employee ID is required';
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.mobile) newErrors.mobile = 'Mobile number is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (!formData.confirm_password) newErrors.confirm_password = 'Please confirm password';
    if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }
    if (!formData.businessId) newErrors.businessId = 'Business ID is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      // Convert businessId to number as per API requirement
      const submitData = {
        ...formData,
        businessId: Number(formData.businessId)
      };

      await registerUser(submitData);
      setAlert({
        show: true,
        message: 'User successfully registered',
        severity: 'success'
      });
      // Reset form
      setFormData({
        username: '',
        user_id: '',
        email: '',
        mobile: '',
        password: '',
        confirm_password: '',
        businessId: '',
        status: 'active',
        is_admin: '',
        terminal: ''
      });
    } catch (error) {
      setAlert({
        show: true,
        message: error.message,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleBusinessIdChange = (event, newValue) => {
    setFormData(prev => ({
      ...prev,
      businessId: newValue ? newValue.value : ''
    }));
    if (errors.businessId) {
      setErrors(prev => ({
        ...prev,
        businessId: ''
      }));
    }
  };

  useEffect(() => {
    let timer;
    if (alert.show) {
      timer = setTimeout(() => {
        setAlert(prev => ({ ...prev, show: false }));
      }, 8000);
    }
    return () => clearTimeout(timer);
  }, [alert.show]);

  return (
    <MainCard title="User Registration">
      {alert.show && (
        <Alert 
          icon={alert.severity === 'success' ? <CheckIcon fontSize="inherit" /> : undefined}
          severity={alert.severity}
          sx={{ mb: 2 }}
          onClose={() => setAlert({ ...alert, show: false })}
        >
          <AlertTitle>{alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}</AlertTitle>
          {alert.message}
        </Alert>
      )}
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
              type="password"
              label="Password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              error={!!errors.password}
              helperText={errors.password}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <CustomInput
              fullWidth
              type="password"
              label="Confirm Password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              error={!!errors.confirm_password}
              helperText={errors.confirm_password}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <CustomAutocomplete
              fullWidth
              options={businessIdOptions}
              getOptionLabel={(option) => option.label}
              value={businessIdOptions.find(option => option.value === formData.businessId) || null}
              onChange={handleBusinessIdChange}
              renderInput={(params) => (
                <CustomInput
                  {...params}
                  label="Business ID"
                  error={!!errors.businessId}
                  helperText={errors.businessId}
                />
              )}
            />
          </Grid>
          <Grid item xs={12}>
            <CustomButton
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              endIcon={<SendIcon />}
            >
              {loading ? 'Registering...' : 'Register User'}
            </CustomButton>
          </Grid>
        </Grid>
      </form>
    </MainCard>
  );
};

export default UserRegister;
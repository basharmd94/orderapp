import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

// material-ui
import { useTheme } from '@mui/material/styles';
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid2';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import InputLabel from '@mui/material/InputLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

// project imports
import AnimateButton from 'ui-component/extended/AnimateButton';
import { apiPost } from 'services/api';

// assets
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

// ===========================|| JWT - REGISTER ||=========================== //

export default function AuthRegister() {
  const theme = useTheme();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [showPassword, setShowPassword] = useState(false);
  const [checked, setChecked] = useState(true);
  const [loading, setLoading] = useState(false);  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    username: '',
    mobile: '',
    user_id: ''
  });

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!checked) {
      enqueueSnackbar('Please agree to the terms and conditions', { variant: 'warning' });
      return;
    }
    
    setLoading(true);
    
    try {
      // Prepare registration data based on API requirements
      const registrationData = {
        username: formData.username || formData.email,
        email: formData.email,
        mobile: formData.mobile || '',
        user_id: formData.user_id || '',
        password: formData.password,
        confirm_password: formData.password,
        status: 'active',
        businessId: 100001,
        is_admin: 'user',
        terminal: '',
        accode: '0'
      };
      
      console.log('Sending registration data:', registrationData);
        // Make registration API call
      const response = await apiPost('/users/registration', registrationData);
      console.log('Registration response:', response);
      
      enqueueSnackbar('Registration successful! Please log in.', { variant: 'success' });
      navigate('/pages/login');
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error.detail || error.message || 'Registration failed. Please try again.';
      enqueueSnackbar(errorMessage, { 
        variant: 'error',
        autoHideDuration: 4000 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container direction="column" spacing={2} sx={{ justifyContent: 'center' }}>
        <Grid container sx={{ alignItems: 'center', justifyContent: 'center' }} size={12}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1">Sign up with Email address</Typography>
          </Box>
        </Grid>
      </Grid>      <Grid container spacing={{ xs: 0, sm: 2 }}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="First Name"
            margin="normal"
            name="firstName"
            type="text"
            value={formData.firstName}
            onChange={handleChange}
            sx={{ ...theme.typography.customInput }}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Last Name"
            margin="normal"
            name="lastName"
            type="text"
            value={formData.lastName}
            onChange={handleChange}
            sx={{ ...theme.typography.customInput }}
          />
        </Grid>
      </Grid>

      <TextField
        fullWidth
        label="Username"
        margin="normal"
        name="username"
        type="text"
        value={formData.username}
        onChange={handleChange}
        sx={{ ...theme.typography.customInput }}
        required
      />

      <Grid container spacing={{ xs: 0, sm: 2 }}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Employee ID"
            margin="normal"
            name="user_id"
            type="text"
            value={formData.user_id}
            onChange={handleChange}
            placeholder="WA--000XXX"
            sx={{ ...theme.typography.customInput }}
            required
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Mobile Number"
            margin="normal"
            name="mobile"
            type="text"
            value={formData.mobile}
            onChange={handleChange}
            sx={{ ...theme.typography.customInput }}
            required
          />
        </Grid>
      </Grid>

      <FormControl fullWidth sx={{ ...theme.typography.customInput }}>
        <InputLabel htmlFor="outlined-adornment-email-register">Email Address</InputLabel>
        <OutlinedInput 
          id="outlined-adornment-email-register" 
          type="email" 
          value={formData.email} 
          name="email" 
          onChange={handleChange}
          inputProps={{}} 
          required
        />
      </FormControl>

      <FormControl fullWidth sx={{ ...theme.typography.customInput }}>
        <InputLabel htmlFor="outlined-adornment-password-register">Password</InputLabel>
        <OutlinedInput
          id="outlined-adornment-password-register"
          type={showPassword ? 'text' : 'password'}
          value={formData.password}
          name="password"
          onChange={handleChange}
          label="Password"
          endAdornment={
            <InputAdornment position="end">
              <IconButton
                aria-label="toggle password visibility"
                onClick={handleClickShowPassword}
                onMouseDown={handleMouseDownPassword}
                edge="end"
                size="large"
              >
                {showPassword ? <Visibility /> : <VisibilityOff />}
              </IconButton>
            </InputAdornment>
          }
          inputProps={{}}
        />
      </FormControl>

      <Grid container sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
        <Grid>
          <FormControlLabel
            control={<Checkbox checked={checked} onChange={(event) => setChecked(event.target.checked)} name="checked" color="primary" />}
            label={
              <Typography variant="subtitle1">
                Agree with &nbsp;
                <Typography variant="subtitle1" component={Link} to="#">
                  Terms & Condition.
                </Typography>
              </Typography>
            }
          />
        </Grid>
      </Grid>

      <Box sx={{ mt: 2 }}>
        <AnimateButton>
          <Button 
            disableElevation 
            fullWidth 
            size="large" 
            type="submit" 
            variant="contained" 
            color="secondary"
            disabled={loading}
          >
            {loading ? 'Signing up...' : 'Sign up'}
          </Button>
        </AnimateButton>
      </Box>
    </form>
  );
}

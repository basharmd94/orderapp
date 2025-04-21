import { useState, useEffect } from 'react';
import { Grid, MenuItem, Box, TextField, InputAdornment } from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import SaveIcon from '@mui/icons-material/Save';
import SearchIcon from '@mui/icons-material/Search';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import { CustomButton, CustomInput } from 'ui-component/custom';
import { apiGet, apiPost, apiDelete, apiPut } from 'services/api';

const ManageUser = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ show: false, message: '', severity: 'success' });
  const [deleteDialog, setDeleteDialog] = useState({ open: false, username: null });
  const [editDialog, setEditDialog] = useState({ open: false, user: null });
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
  const [updating, setUpdating] = useState(false);
  
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

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await apiGet('/admin/user-manage/get-all-users');  // Updated endpoint
      if (!response) {
        throw new Error('No data received from server');
      }
      console.log('Users data:', response); // Debug log
      setUsers(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error fetching users:', error);
      setUsers([]);
      setAlert({
        show: true,
        message: error?.detail || error?.message || 'Error fetching users',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    let timer;
    if (alert.show) {
      timer = setTimeout(() => {
        setAlert(prev => ({ ...prev, show: false }));
      }, 5000);
    }
    return () => clearTimeout(timer);
  }, [alert.show]);
  
  // Open edit dialog and populate form with user data
  const handleEditUser = (user) => {
    setFormData({
      username: user.username,
      email: user.email,
      mobile: user.mobile || '',
      user_id: user.user_id || user.employeeCode || '',
      status: user.status || 'active',
      businessId: user.businessId?.toString() || '',
      is_admin: user.is_admin || 'user',
      password: '' // Password is always empty initially
    });
    setEditDialog({ open: true, user });
    setErrors({});
  };
  
  // Handle form field changes
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
  
  // Handle form submission to update user
  const handleUpdateUser = async () => {
    // Validate form
    const newErrors = {};
    if (!formData.email) newErrors.email = 'Email is required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setUpdating(true);
    
    try {
      // Build update data - exclude empty password
      const updateData = { ...formData };
      
      // Only include password if provided
      if (!updateData.password) {
        delete updateData.password;
      }
      
      // Convert businessId to number
      if (updateData.businessId) {
        updateData.businessId = Number(updateData.businessId);      }

      // Make the API call
      const response = await apiPut('/admin/user-manage/update-user', updateData);
      
      setAlert({
        show: true,
        message: response.message || 'User updated successfully',
        severity: 'success'
      });
      
      // Close dialog and refresh user list
      setEditDialog({ open: false, user: null });
      fetchUsers();
    } catch (error) {
      console.error('Update error:', error);
      setAlert({
        show: true,
        message: error.detail || error.message || 'Error updating user',
        severity: 'error'
      });
    } finally {
      setUpdating(false);
    }
  };

  const handleStatusUpdate = async (username, newStatus) => {
    try {
      await apiPost('/admin/user-manage/status', {  // Updated endpoint
        username,
        status: newStatus
      });
      setAlert({
        show: true,
        message: `User status updated successfully`,
        severity: 'success'
      });
      fetchUsers(); // Refresh the user list
    } catch (error) {
      setAlert({
        show: true,
        message: error.response?.data?.detail || 'Error updating user status',
        severity: 'error'
      });
    }
  };

  const handleDelete = async (username) => {
    try {
      await apiDelete(`/admin/user-manage/${username}`);  // Updated endpoint
      setAlert({
        show: true,
        message: 'User deleted successfully',
        severity: 'success'
      });
      fetchUsers(); // Refresh the user list
    } catch (error) {
      setAlert({
        show: true,
        message: error.response?.data?.detail || 'Error deleting user',
        severity: 'error'
      });
    } finally {
      setDeleteDialog({ open: false, username: null });
    }
  };

  const columns = [
    { field: 'username', headerName: 'Username', flex: 1 },
    { field: 'email', headerName: 'Email', flex: 1.5 },
    { field: 'user_id', headerName: 'Employee ID', flex: 1 },
    { field: 'businessId', headerName: 'Business ID', flex: 1 },
    { field: 'is_admin', headerName: 'Role', flex: 0.7 },
    { field: 'status', headerName: 'Status', flex: 0.7 },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 1,
      sortable: false,      renderCell: (params) => (
        <div>
          <IconButton 
            color="primary" 
            onClick={() => handleEditUser(params.row)}
            title="Edit User"
          >
            <EditIcon />
          </IconButton>
          <IconButton 
            color="error" 
            onClick={() => setDeleteDialog({ open: true, username: params.row.username })}
            title="Delete User"
          >
            <DeleteIcon />
          </IconButton>
          <IconButton
            color={params.row.status === 'active' ? 'error' : 'success'}
            onClick={() => handleStatusUpdate(
              params.row.username, 
              params.row.status === 'active' ? 'inactive' : 'active'
            )}
            title={params.row.status === 'active' ? 'Deactivate User' : 'Activate User'}
          >
            {params.row.status === 'active' ? <BlockIcon /> : <CheckCircleIcon />}
          </IconButton>
        </div>
      )
    }
  ];

  return (
    <MainCard title="Manage Users">
      {alert.show && (
        <Alert 
          severity={alert.severity}
          sx={{ mb: 2 }}
          onClose={() => setAlert({ ...alert, show: false })}
        >
          <AlertTitle>{alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}</AlertTitle>
          {alert.message}
        </Alert>      )}
      
      <div style={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={(users || []).map(user => ({ ...user, id: user.username }))}
          columns={columns}
          initialState={{
            pagination: {
              paginationModel: { pageSize: 10, page: 0 },
            },
          }}
          pageSizeOptions={[10, 25, 50]}
          disableRowSelectionOnClick
          loading={loading}
          slots={{ toolbar: GridToolbar }}
          slotProps={{
            toolbar: {
              showQuickFilter: true,
              quickFilterProps: { debounceMs: 300 },
              csvOptions: { disableToolbarButton: true },
              printOptions: { disableToolbarButton: true }
            }
          }}
        />
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, username: null })}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete user "{deleteDialog.username}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, username: null })}>Cancel</Button>
          <Button 
            onClick={() => handleDelete(deleteDialog.username)} 
            color="error" 
            variant="contained"
          >
            Delete          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog
        open={editDialog.open}
        onClose={() => setEditDialog({ open: false, user: null })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          {editDialog.user && (
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <CustomInput
                  fullWidth
                  label="Username"
                  name="username"
                  value={formData.username}
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
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ open: false, user: null })}>Cancel</Button>
          <Button 
            onClick={handleUpdateUser} 
            color="primary" 
            variant="contained"
            disabled={updating}
            startIcon={updating ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            {updating ? 'Updating...' : 'Update User'}
          </Button>
        </DialogActions>
      </Dialog>
    </MainCard>
  );
};

export default ManageUser;
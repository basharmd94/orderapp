import { useState, useEffect } from 'react';
import { Grid } from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import { DataGrid } from '@mui/x-data-grid';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import BlockIcon from '@mui/icons-material/Block';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import { CustomButton } from 'ui-component/custom';
import { apiGet, apiPost, apiDelete } from 'services/api';

const ManageUser = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ show: false, message: '', severity: 'success' });
  const [deleteDialog, setDeleteDialog] = useState({ open: false, username: null });

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
      sortable: false,
      renderCell: (params) => (
        <div>
          <IconButton 
            color="primary" 
            onClick={() => console.log('Edit user:', params.row.username)}
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
        </Alert>
      )}
      
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
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </MainCard>
  );
};

export default ManageUser;
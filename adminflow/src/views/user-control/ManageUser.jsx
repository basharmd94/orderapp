import { useState, useEffect } from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  IconButton,
  Chip,
  InputAdornment,
  Stack
} from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import { CustomInput, CustomButton } from 'ui-component/custom';
import { IconEdit, IconTrash, IconSearch, IconRefresh } from '@tabler/icons-react';

const ManageUser = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  useEffect(() => {
    // TODO: Fetch users data
    setLoading(false);
  }, []);

  const handleEdit = (userId) => {
    // TODO: Implement edit functionality
    console.log('Edit user:', userId);
  };

  const handleDelete = (userId) => {
    // TODO: Implement delete functionality
    console.log('Delete user:', userId);
  };

  const handleRefresh = () => {
    // TODO: Implement refresh functionality
    setLoading(true);
    // Simulating refresh
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <MainCard 
      title="Manage Users"
      secondary={
        <CustomButton
          variant="contained"
          startIcon={<IconRefresh size={20} />}
          onClick={handleRefresh}
          disabled={loading}
        >
          Refresh
        </CustomButton>
      }
    >
      <Stack spacing={3}>
        <CustomInput
          fullWidth
          variant="outlined"
          placeholder="Search users..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ maxWidth: 500 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <IconSearch stroke={1.5} size="20px" />
              </InputAdornment>
            )
          }}
        />
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Username</TableCell>
                <TableCell>Employee ID</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Business ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {/* TODO: Replace with actual data */}
              <TableRow>
                <TableCell>John Doe</TableCell>
                <TableCell>EMP001</TableCell>
                <TableCell>john@example.com</TableCell>
                <TableCell>100000</TableCell>
                <TableCell>
                  <Chip label="Active" color="success" size="small" />
                </TableCell>
                <TableCell align="center">
                  <CustomButton
                    variant="outlined"
                    size="small"
                    startIcon={<IconEdit stroke={1.5} size="16px" />}
                    onClick={() => handleEdit('1')}
                    sx={{ mr: 1 }}
                  >
                    Edit
                  </CustomButton>
                  <CustomButton
                    variant="outlined"
                    size="small"
                    color="error"
                    startIcon={<IconTrash stroke={1.5} size="16px" />}
                    onClick={() => handleDelete('1')}
                  >
                    Delete
                  </CustomButton>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Stack>
    </MainCard>
  );
};

export default ManageUser;
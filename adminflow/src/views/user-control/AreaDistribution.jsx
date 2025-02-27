import { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  Chip
} from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import { CustomInput, CustomButton, CustomAutocomplete } from 'ui-component/custom';
import { IconMapPin, IconUserCheck } from '@tabler/icons-react';

const AreaDistribution = () => {
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedArea, setSelectedArea] = useState(null);
  const [assignments, setAssignments] = useState([]);

  const users = [
    { id: '1', label: 'John Doe' },
    { id: '2', label: 'Jane Smith' }
  ];

  const areas = [
    { id: 'A1', label: 'Area 1' },
    { id: 'A2', label: 'Area 2' }
  ];

  const handleAssign = () => {
    if (selectedUser && selectedArea) {
      setAssignments(prev => [
        ...prev,
        {
          id: Date.now(),
          userId: selectedUser.id,
          userName: selectedUser.label,
          areaCode: selectedArea.id,
          areaName: selectedArea.label,
          assignedDate: new Date().toLocaleDateString()
        }
      ]);
      setSelectedUser(null);
      setSelectedArea(null);
    }
  };

  return (
    <MainCard title="Area Distribution">
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h4" gutterBottom>
                Assign Area
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <CustomAutocomplete
                    fullWidth
                    options={users}
                    value={selectedUser}
                    onChange={(_, newValue) => setSelectedUser(newValue)}
                    renderInput={(params) => (
                      <CustomInput
                        {...params}
                        label="Select User"
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <CustomAutocomplete
                    fullWidth
                    options={areas}
                    value={selectedArea}
                    onChange={(_, newValue) => setSelectedArea(newValue)}
                    renderInput={(params) => (
                      <CustomInput
                        {...params}
                        label="Select Area"
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <CustomButton
                    variant="contained"
                    disabled={!selectedUser || !selectedArea}
                    onClick={handleAssign}
                    startIcon={<IconMapPin />}
                  >
                    Assign Area
                  </CustomButton>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <IconUserCheck size={24} />
                <Typography variant="h4">
                  Current Assignments
                </Typography>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell>Area</TableCell>
                      <TableCell>Assigned Date</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {assignments.map((assignment) => (
                      <TableRow key={assignment.id}>
                        <TableCell>{assignment.userName}</TableCell>
                        <TableCell>{assignment.areaName}</TableCell>
                        <TableCell>{assignment.assignedDate}</TableCell>
                        <TableCell>
                          <Chip label="Active" color="success" size="small" />
                        </TableCell>
                      </TableRow>
                    ))}
                    {assignments.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          No assignments found
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </MainCard>
  );
};

export default AreaDistribution;
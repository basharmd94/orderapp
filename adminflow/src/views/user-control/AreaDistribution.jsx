import { useState, useEffect } from 'react';
import { Grid, CircularProgress } from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import { CustomInput, CustomButton, CustomAutocomplete } from 'ui-component/custom';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import { apiPost } from 'services/api';

const AreaDistribution = () => {
  const [formData, setFormData] = useState({
    zid: '',
    area: '',
    xsp: '',
    xsp1: '',
    xsp2: '',
    xsp3: ''
  });
  
  const [areas, setAreas] = useState([]);
  const [alert, setAlert] = useState({ show: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState({
    areas: false,
    salesmen: false,
    submit: false
  });
  const [showSalesmenInputs, setShowSalesmenInputs] = useState(false);

  const businessIdOptions = [
    { label: '100000', value: '100000' },
    { label: '100001', value: '100001' },
    { label: '100005', value: '100005' }
  ];

  const fetchAreas = async (zid) => {
    try {
      setLoading(prev => ({ ...prev, areas: true }));
      const response = await apiPost('/customers/get-area-by-zid', { zid });
      setAreas(response.areas.map(area => ({ label: area, value: area })));
    } catch (error) {
      setAlert({
        show: true,
        message: error?.detail || 'Error fetching areas',
        severity: 'error'
      });
      setAreas([]);
    } finally {
      setLoading(prev => ({ ...prev, areas: false }));
    }
  };

  const fetchSalesmen = async () => {
    try {
      setLoading(prev => ({ ...prev, salesmen: true }));
      const response = await apiPost('/customers/get-salesman-area-wise', {
        zid: Number(formData.zid),
        area: formData.area
      });
      
      setFormData(prev => ({
        ...prev,
        xsp: response.xsp || '',
        xsp1: response.xsp1 || '',
        xsp2: response.xsp2 || '',
        xsp3: response.xsp3 || ''
      }));
      setShowSalesmenInputs(true);
    } catch (error) {
      setAlert({
        show: true,
        message: error?.detail || 'Error fetching salesman information',
        severity: 'error'
      });
    } finally {
      setLoading(prev => ({ ...prev, salesmen: false }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(prev => ({ ...prev, submit: true }));
      await apiPost('/customers/update-salesman-area-wise', {
        ...formData,
        zid: Number(formData.zid)
      });
      setAlert({
        show: true,
        message: 'Salesman assignments updated successfully',
        severity: 'success'
      });
    } catch (error) {
      setAlert({
        show: true,
        message: error?.detail || 'Error updating salesman assignments',
        severity: 'error'
      });
    } finally {
      setLoading(prev => ({ ...prev, submit: false }));
    }
  };

  const handleZidChange = (event, newValue) => {
    setFormData(prev => ({
      ...prev,
      zid: newValue?.value || '',
      area: '', // Reset area when zid changes
      xsp: '',  // Reset salesman fields
      xsp1: '',
      xsp2: '',
      xsp3: ''
    }));
    setShowSalesmenInputs(false);
    if (newValue?.value) {
      fetchAreas(Number(newValue.value));
    } else {
      setAreas([]);
    }
  };

  const handleAreaChange = (event, newValue) => {
    setFormData(prev => ({
      ...prev,
      area: newValue?.value || '',
      xsp: '',  // Reset salesman fields
      xsp1: '',
      xsp2: '',
      xsp3: ''
    }));
    if (newValue?.value) {
      fetchSalesmen();
    } else {
      setShowSalesmenInputs(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  useEffect(() => {
    let timer;
    if (alert.show) {
      timer = setTimeout(() => {
        setAlert(prev => ({ ...prev, show: false }));
      }, 5000);
    }
    return () => clearTimeout(timer);
  }, [alert.show]);

  return (
    <MainCard title="Area Distribution">
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

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <CustomAutocomplete
              fullWidth
              options={businessIdOptions}
              getOptionLabel={(option) => option.label}
              value={businessIdOptions.find(option => option.value === formData.zid) || null}
              onChange={handleZidChange}
              renderInput={(params) => (
                <CustomInput
                  {...params}
                  label="Business ID"
                  required
                  placeholder="Select Business ID"
                />
              )}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <CustomAutocomplete
              fullWidth
              options={areas}
              getOptionLabel={(option) => option.label}
              value={areas.find(option => option.value === formData.area) || null}
              onChange={handleAreaChange}
              loading={loading.areas}
              loadingText="Loading areas..."
              disabled={!formData.zid || loading.areas}
              noOptionsText={formData.zid ? "No areas found" : "Select a Business ID first"}
              renderInput={(params) => (
                <CustomInput
                  {...params}
                  label="Select Area"
                  required
                  placeholder={formData.zid ? "Select area" : "Select Business ID first"}
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {loading.areas ? <CircularProgress color="inherit" size={20} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
          </Grid>

          {loading.salesmen && (
            <Grid item xs={12} sx={{ textAlign: 'center', py: 3 }}>
              <CircularProgress />
            </Grid>
          )}

          {showSalesmenInputs && (
            <>
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Update salesman assignments for area: {formData.area}
                </Alert>
              </Grid>
              <Grid item xs={12} md={6}>
                <CustomInput
                  fullWidth
                  label="Salesman 1 (xsp)"
                  name="xsp"
                  value={formData.xsp}
                  onChange={handleInputChange}
                  placeholder="Enter salesman ID"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <CustomInput
                  fullWidth
                  label="Salesman 2 (xsp1)"
                  name="xsp1"
                  value={formData.xsp1}
                  onChange={handleInputChange}
                  placeholder="Enter salesman ID"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <CustomInput
                  fullWidth
                  label="Salesman 3 (xsp2)"
                  name="xsp2"
                  value={formData.xsp2}
                  onChange={handleInputChange}
                  placeholder="Enter salesman ID"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <CustomInput
                  fullWidth
                  label="Salesman 4 (xsp3)"
                  name="xsp3"
                  value={formData.xsp3}
                  onChange={handleInputChange}
                  placeholder="Enter salesman ID"
                />
              </Grid>
              <Grid item xs={12}>
                <CustomButton
                  type="submit"
                  variant="contained"
                  disabled={loading.submit}
                  sx={{ mt: 2 }}
                >
                  {loading.submit ? (
                    <>
                      <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
                      Updating...
                    </>
                  ) : (
                    'Update Salesman Distribution'
                  )}
                </CustomButton>
              </Grid>
            </>
          )}
        </Grid>
      </form>
    </MainCard>
  );
};

export default AreaDistribution;
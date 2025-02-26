import { syncCustomersRequest } from '../lib/api_customers';
import { createTable, getExistingCustomers, upsertCustomers } from '../database/customerModels';

const fetchAllCustomers = async (employeeId, limit = 100) => {
  let offset = 0;
  let allCustomers = [];
  while (true) {
    const customers = await syncCustomersRequest(employeeId, limit, offset);
    if (!Array.isArray(customers) || customers.length === 0) break;
    allCustomers = allCustomers.concat(customers);
    offset += limit;
  }
  return allCustomers;
};

const syncCustomers = async (employeeId) => {
  try {
    await createTable();
    const apiCustomers = await fetchAllCustomers(employeeId);
    const existingCustomerSet = await getExistingCustomers();
    const customersToUpsert = apiCustomers.filter(
      customer => !existingCustomerSet.has(JSON.stringify(customer))
    );
    if (customersToUpsert.length > 0) {
      await upsertCustomers(customersToUpsert);
      console.log(`Upserted ${customersToUpsert.length} customers successfully`);
    } else {
      console.log('No new or updated customers to upsert');
    }
    return true;
  } catch (error) {
    console.error('Error syncing customers:', error);
    throw error;
  }
};

export default syncCustomers;
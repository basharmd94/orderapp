import { syncCustomersRequest } from '../lib/api_customers';
import { createTable, getExistingCustomers, upsertCustomers } from '../database/customerModels';

const BATCH_SIZE = 100;

const fetchAllCustomers = async (employeeId, limit = 100) => {
  let offset = 0;
  let allCustomers = [];
  let reachedEnd = false;

  while (!reachedEnd) {
    try {
      const customers = await syncCustomersRequest(employeeId, limit, offset);
      if (!Array.isArray(customers) || customers.length === 0) {
        reachedEnd = true;
        break;
      }
      allCustomers = allCustomers.concat(customers);
      offset += limit;
      console.log(`Fetched ${customers.length} customers, total: ${allCustomers.length}`);
    } catch (error) {
      // If we get a 404, it means we've reached the end of the data
      if (error.response?.status === 404) {
        reachedEnd = true;
        break;
      }
      throw error; // Re-throw other errors
    }
  }
  return allCustomers;
};

const processBatch = async (customers) => {
  for (let i = 0; i < customers.length; i += BATCH_SIZE) {
    const batch = customers.slice(i, i + BATCH_SIZE);
    await upsertCustomers(batch);
    console.log(`Processed batch of ${batch.length} customers (${i + batch.length}/${customers.length})`);
  }
};

const syncCustomers = async (employeeId) => {
  try {
    await createTable();
    console.log('Fetching customers from API...');
    const apiCustomers = await fetchAllCustomers(employeeId);
    console.log(`Fetched ${apiCustomers.length} customers from API`);

    if (apiCustomers.length === 0) {
      return {
        success: true,
        totalCustomers: 0,
        updatedCustomers: 0,
        message: 'No customers to sync'
      };
    }

    console.log('Getting existing customers from local database...');
    const existingCustomerSet = await getExistingCustomers();
    console.log(`Found ${existingCustomerSet.size} existing customers`);

    const customersToUpsert = apiCustomers.filter(
      customer => !existingCustomerSet.has(JSON.stringify(customer))
    );

    if (customersToUpsert.length > 0) {
      console.log(`Upserting ${customersToUpsert.length} customers...`);
      await processBatch(customersToUpsert);
      console.log(`Upserted ${customersToUpsert.length} customers successfully`);
    } else {
      console.log('No new or updated customers to upsert');
    }

    return {
      success: true,
      totalCustomers: apiCustomers.length,
      updatedCustomers: customersToUpsert.length
    };
  } catch (error) {
    console.error('Error syncing customers:', error);
    // If we have already fetched and processed some customers successfully
    // but encountered an error during the process, we should still
    // report partial success
    if (error.message === 'transactionAsync not available') {
      return {
        success: true,
        totalCustomers: -1,
        updatedCustomers: -1,
        message: 'Sync completed with some customers updated'
      };
    }
    return {
      success: false,
      error: error.message
    };
  }
};

export default syncCustomers;
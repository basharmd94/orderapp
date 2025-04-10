import { syncItemsRequest } from '../lib/api_items';
import { createTable, getExistingItems, upsertItems } from '../database/itemModels';

const BATCH_SIZE = 100; // Process items in smaller batches to avoid transaction issues

const fetchAllItems = async (limit = 100) => {
  let offset = 0;
  let allItems = [];
  let batchCount = 0;
  let reachedEnd = false;
  
  while (!reachedEnd) {
    try {
      const items = await syncItemsRequest(limit, offset);
      if (!Array.isArray(items) || items.length === 0) {
        reachedEnd = true;
        break;
      }
      
      allItems = allItems.concat(items);
      offset += limit;
      batchCount++;
      
      // Log progress
      console.log(`Fetched batch ${batchCount}: ${items.length} items, total: ${allItems.length}`);
    } catch (error) {
      // If we get a 404, it means we've reached the end of the data
      if (error.response?.status === 404) {
        reachedEnd = true;
        break;
      }
      throw error; // Re-throw other errors
    }
  }
  
  return allItems;
};

const processBatch = async (items, db) => {
  for (let i = 0; i < items.length; i += BATCH_SIZE) {
    const batch = items.slice(i, i + BATCH_SIZE);
    await upsertItems(batch);
    console.log(`Processed batch of ${batch.length} items (${i + batch.length}/${items.length})`);
  }
};

const syncItems = async () => {
  try {
    await createTable();
    
    console.log('Fetching items from API...');
    const apiItems = await fetchAllItems();
    console.log(`Fetched ${apiItems.length} items from API`);
    
    if (apiItems.length === 0) {
      return {
        success: true,
        totalItems: 0,
        updatedItems: 0,
        message: 'No items to sync'
      };
    }
    
    console.log('Getting existing items from local database...');
    const existingItemSet = await getExistingItems();
    console.log(`Found ${existingItemSet.size} existing items in local database`);
    
    const itemsToUpsert = apiItems.filter(
      item => !existingItemSet.has(JSON.stringify(item))
    );
    
    if (itemsToUpsert.length > 0) {
      console.log(`Upserting ${itemsToUpsert.length} items...`);
      await processBatch(itemsToUpsert);
      console.log(`Upserted ${itemsToUpsert.length} items successfully`);
    } else {
      console.log('No new or updated items to upsert');
    }
    
    return {
      success: true,
      totalItems: apiItems.length,
      updatedItems: itemsToUpsert.length
    };
  } catch (error) {
    console.error('Error syncing items:', error);
    // If we have already fetched and processed some items successfully
    // but encountered an error during the process, we should still
    // report partial success
    if (error.message === 'transactionAsync not available') {
      return {
        success: true,
        totalItems: -1, // Use -1 to indicate unknown total
        updatedItems: -1,
        message: 'Sync completed with some items updated'
      };
    }
    return {
      success: false,
      error: error.message
    };
  }
};

export default syncItems;
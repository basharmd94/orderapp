import getDatabase from './database';

const createTable = async () => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  const query = `
    CREATE TABLE IF NOT EXISTS item (
      zid INTEGER,
      item_id TEXT,
      item_name TEXT,
      item_group TEXT,
      std_price REAL,
      stock REAL,
      min_disc_qty REAL,
      disc_amt REAL
    )
  `;
  await db.execAsync(query);
};

const getExistingItems = async () => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  const rows = await db.getAllAsync('SELECT * FROM item');
  return new Set(rows.map(row => JSON.stringify({
    zid: row.zid,
    item_id: row.item_id,
    item_name: row.item_name,
    item_group: row.item_group,
    std_price: row.std_price,
    stock: row.stock,
    min_disc_qty: row.min_disc_qty,
    disc_amt: row.disc_amt
  })));
};

const upsertItems = async (items) => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  if (!db.transactionAsync) throw new Error('transactionAsync not available');
  const statement = `
    INSERT OR REPLACE INTO item 
    (zid, item_id, item_name, item_group, std_price, stock, min_disc_qty, disc_amt) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;
  await db.transactionAsync(async (tx) => {
    for (const item of items) {
      await tx.runAsync(statement, [
        item.zid,
        item.item_id,
        item.item_name,
        item.item_group,
        item.std_price,
        item.stock,
        item.min_disc_qty,
        item.disc_amt
      ]);
    }
  });
};

const getItems = async (zid, searchText, limit = 20, offset = 0) => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  
  let query = 'SELECT * FROM item WHERE zid = ?';
  const params = [zid];
  
  if (searchText && searchText.length > 0) {
    query += ' AND (item_name LIKE ? OR item_id LIKE ?)';
    params.push(`%${searchText}%`, `%${searchText}%`);
  }
  
  query += ' ORDER BY item_name LIMIT ? OFFSET ?';
  params.push(limit, offset);
  
  return await db.getAllAsync(query, params);
};

export { createTable, getExistingItems, upsertItems, getItems };
import getDatabase from './database';

const createTable = async () => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  const query = `
    CREATE TABLE IF NOT EXISTS customer (
      zid INTEGER,
      xcus TEXT,
      xorg TEXT,
      xadd1 TEXT,
      xcity TEXT,
      xstate TEXT,
      xmobile TEXT,
      xtaxnum TEXT,
      xsp TEXT,
      xsp1 TEXT,
      xsp2 TEXT,
      xsp3 TEXT
    )
  `;
  await db.execAsync(query);
};

const getExistingCustomers = async () => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  const rows = await db.getAllAsync('SELECT * FROM customer');
  return new Set(rows.map(row => JSON.stringify({
    zid: row.zid,
    xcus: row.xcus,
    xorg: row.xorg,
    xadd1: row.xadd1,
    xcity: row.xcity,
    xstate: row.xstate,
    xmobile: row.xmobile,
    xtaxnum: row.xtaxnum,
    xsp: row.xsp,
    xsp1: row.xsp1,
    xsp2: row.xsp2,
    xsp3: row.xsp3
  })));
};

const upsertCustomers = async (customers) => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  
  const statement = `
    INSERT OR REPLACE INTO customer 
    (zid, xcus, xorg, xadd1, xcity, xstate, xmobile, xtaxnum, xsp, xsp1, xsp2, xsp3) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `;
  
  for (const customer of customers) {
    await db.runAsync(statement, [
      customer.zid,
      customer.xcus,
      customer.xorg,
      customer.xadd1,
      customer.xcity,
      customer.xstate,
      customer.xmobile,
      customer.xtaxnum,
      customer.xsp,
      customer.xsp1,
      customer.xsp2,
      customer.xsp3
    ]);
  }
};

const getCustomers = async (zid, searchText, userId, limit = 40, offset = 0) => {
  const db = await getDatabase();
  if (!db) throw new Error('Database not initialized');
  
  let query = 'SELECT * FROM customer WHERE zid = ?';
  const params = [zid];
  
  if (searchText && searchText.length > 0) {
    query += ' AND (xorg LIKE ? OR xcus LIKE ?)';
    params.push(`%${searchText}%`, `%${searchText}%`);
  }

  // Add user-specific filter for salesperson
  if (userId) {
    query += ' AND (xsp = ? OR xsp1 = ? OR xsp2 = ? OR xsp3 = ?)';
    params.push(userId, userId, userId, userId);
  }
  
  query += ' ORDER BY xcus LIMIT ? OFFSET ?';
  params.push(limit, offset);
  
  return await db.getAllAsync(query, params);
};

export { createTable, getExistingCustomers, upsertCustomers, getCustomers };
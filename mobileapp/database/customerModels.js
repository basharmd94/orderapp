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
  if (!db.transactionAsync) throw new Error('transactionAsync not available');
  const statement = `
    INSERT OR REPLACE INTO customer 
    (zid, xcus, xorg, xadd1, xcity, xstate, xmobile, xtaxnum, xsp, xsp1, xsp2, xsp3) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `;
  await db.transactionAsync(async (tx) => {
    for (const customer of customers) {
      await tx.runAsync(statement, [
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
  });
};

export { createTable, getExistingCustomers, upsertCustomers };
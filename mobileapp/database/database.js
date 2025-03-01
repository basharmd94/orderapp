import * as SQLite from 'expo-sqlite';

let database;

const getDatabase = async () => {
  if (!database) {
    console.log('Opening database...');
    try {
      database = await SQLite.openDatabaseAsync('da.db');
      
      // Enable WAL mode for better performance
      await database.execAsync('PRAGMA journal_mode = WAL');
      
      // Add async query support
      database.execAsync = database.execAsync || 
        ((query) => database.exec([{ sql: query, args: [] }], false));
      
      // Add async getAll support if not provided
      database.getAllAsync = database.getAllAsync || 
        ((query, params = []) => {
          return new Promise((resolve, reject) => {
            database.transaction(tx => {
              tx.executeSql(
                query,
                params,
                (_, { rows: { _array } }) => resolve(_array),
                (_, error) => reject(error)
              );
            });
          });
        });

      // Add async run support for single operations if not provided
      database.runAsync = database.runAsync || 
        ((query, params = []) => {
          return new Promise((resolve, reject) => {
            database.transaction(tx => {
              tx.executeSql(
                query,
                params,
                (_, result) => resolve(result),
                (_, error) => reject(error)
              );
            });
          });
        });

      console.log('Database initialized with async operations');
    } catch (error) {
      console.error('Error initializing database:', error);
      throw error;
    }
  }
  return database;
};

export default getDatabase;
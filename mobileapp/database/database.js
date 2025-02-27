import * as SQLite from 'expo-sqlite';

let database;

const getDatabase = async () => {
  if (!database) {
    console.log('Opening database...');
    database = await SQLite.openDatabaseAsync('da.db');
    console.log('Database opened:', database);
    if (!database.transactionAsync) {
      console.error('transactionAsync not available on db:', database);
    }
  }
  return database;
};

export default getDatabase;
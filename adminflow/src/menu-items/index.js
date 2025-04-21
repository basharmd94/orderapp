import dashboard from './dashboard';
import pages from './pages';
import utilities from './utilities';
import other from './other';
import getUsersMenu from './users'; // Notice the change here - importing the function

const menuItems = {
  // MENU CONFIGURATION:
  // Some menu items are temporarily hidden but code is preserved
  // To restore hidden items, simply uncomment them in the array below
  items: [
    // dashboard,  // HIDDEN: Dashboard menu item
    getUsersMenu, 
    // pages,      // HIDDEN: Pages/Authentication menu items
    // utilities,  // HIDDEN: Utilities menu items
    other
  ] // getUsersMenu is now a function
};

export default menuItems;
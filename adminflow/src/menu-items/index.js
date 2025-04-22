import dashboard from './dashboard';
import pages from './pages';
import utilities from './utilities';
import other from './other';
import getUsersMenu from './users'; // Notice the change here - importing the function

const menuItems = {
  items: [dashboard, getUsersMenu, pages, utilities, other] // getUsersMenu is now a function
};

export default menuItems;
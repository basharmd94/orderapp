from database import get_db
from models.users_model import ApiUsers ,UrlRoutes 

class DatabaseController:
    def __init__(self):
        self.db = next(get_db())

    def get_user_by_username(self, username: str) -> ApiUsers:
        return self.db.query(ApiUsers).filter(ApiUsers.username == username).first()

    
    def get_urlroute_by_path(self, path: str) -> UrlRoutes:
        return self.db.query(UrlRoutes).filter(UrlRoutes.urldb == path).first()
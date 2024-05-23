from database import get_db


class DatabaseController:
    def __init__(self):
        self.db = next(get_db())

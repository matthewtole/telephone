from ..database import Database
from base import Telephone


class TelephoneDesktop(Telephone):
    def __init__(self, db: Database) -> None:
        super().__init__(db)

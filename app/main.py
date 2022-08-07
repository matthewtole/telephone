from database import Database
from telephone import Telephone

if __name__ == "__main__":
    db = Database("telephone.db")
    db.create_tables()
    telephone = Telephone(db)
    telephone.test()

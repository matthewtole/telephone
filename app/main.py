from telephone import Telephone
from database import Database

if __name__ == '__main__':
    db = Database("telephone.db")
    db.create_tables()
    telephone = Telephone(db)
    telephone.test()
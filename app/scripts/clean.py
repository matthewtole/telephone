
from os import listdir, path, unlink
from database import Database
from config import DATABASE_FILE


def clean_messages():
    db: Database = Database(DATABASE_FILE)
    messages = listdir("messages")
    for filename in messages:
        m = db.messages.get_by_filename(filename)
        if m is None:
            unlink(path.join("messages", filename))
            print("Deleting %s" % filename)

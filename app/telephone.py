from input import Input
from database import Database


class Telephone:
    def __init__(self, database: Database, input: Input):
        self.database = database
        self.input = input

    def tick(self):
        button = self.input.button_pressed()
        if button is None:
            pass
        else:
            print("Button: %s" % button)

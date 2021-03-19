# file mygame/typeclasses/errāre_script.py

from evennia import DefaultScript

class ErrāreScript(DefaultScript):

    def at_script_creation(self):
        self.key = "errāre"
        self.interval = 60
        self.persistent = True
#        self.repeats = 1

    def at_repeat(self):
        self.obj.goto_next_room()

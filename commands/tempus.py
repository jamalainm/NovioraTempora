import datetime
from evennia.utils import gametime

from commands.command import Command

class Tempus(Command):

    """
    Display the time.

    Syntax:
        tempus

    """

    key = "tempus"
    locks = "cmd:all()"

    def func(self):
        """ Execute the time command. """

        tempus = datetime.datetime.fromtimestamp(gametime.gametime(absolute=True))
        hōra = tempus.hour
        if hōra > 18 or hōra < 6:
            self.msg("Nox est.")
        else:
            self.msg(f"Nunc est hōra {hōra - 5}.")
#        year, month, day, hour, min, sec = datetime.datetime.fromtimestamp(gametime.gametime(absolute=True))
#        self.msg(f"Nunc est hōra {tempus.hour}.")

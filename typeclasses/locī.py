"""
Room

Rooms are simple containers that has no location of their own.

"""
from collections import defaultdict

# from evennia import DefaultRoom
from evennia.contrib.ingame_python.typeclasses import EventRoom

from utils.latin_language.populate_forms import populate_forms
from utils.latin_language.list_to_string import list_to_string
from utils.latin_language.get_numbered_name import get_numbered_name

from evennia.utils import ansi, gametime

# from typeclasses.inflected_noun import InflectedNoun

class Locus(EventRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def basetype_posthook_setup(self):

        # add all of the case endings to attributes
        if hasattr(self, 'db'):
            if self.db.formae:
                if len(self.db.formae['nom_sg']) > 1:
                    nōmen_nom = self.db.formae['nom_sg'][1]
                    nōmen_gen = self.db.formae['gen_sg'][1]


                nominative = self.db.formae['nom_sg'][0]
                genitive = self.db.formae['gen_sg'][0]
                sexus = self.db.sexus

                populate_forms(self, nom=nominative, gen=genitive, gender=sexus)

                # Check if there is a nōmen for this character
                if len(self.db.formae['nom_sg']) > 1:

                    populate_forms(self, nom=nōmen_nom, gen=nōmen_gen, gender=sexus)

                self.db.Latin = True
    
    def return_appearance(self, looker, **kwargs):
        """
        # Lightly editing to change "You see" to "Ecce"
        # and 'Exits' to 'Ad hos locos ire potes:'
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """


        if not looker:
            return ""
        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        colorful_exits = []
        # adjusted the exit name to take out the dbref so builders can
        # click on the exits to go there
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(con.key)
                if con.is_typeclass("typeclasses.iānuae.Iānua",exact=False):
                    if con.db.closed == True:
                        colorful_exits.append(f"|lc{con.key}|lt|g[{con.key}]|n|le")
                    else:
                        colorful_exits.append(f"|lc{con.key}|lt|g{con.key}|n|le")
                else:
                    colorful_exits.append(f"|lc{con.key}|lt|g{con.key}|n|le")
            elif con.has_account:
                if con.db.ardēns:
                    users.append("|y(ardēns)|n |c%s|n" % key)
                else:
                    users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)

        # get description, build string
        string = "\n|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc

        if desc:
            string += "%s\n" % desc

        if exits:
            # Changing this string so that exits appear green
            # string += "\n|wAd hos locos potes ire:|n\n " + LatinNoun.list_to_string(exits)
#            colorful_exits = []
#            for exit in exits:
#                colorful_exits.append(f"|lc{exit}|lt|g{exit}|n|le")
            colorful_exits = sorted(colorful_exits)
            string += "\n|wAd hōs locōs īre licet:|n\n " + list_to_string(colorful_exits) + "\n"
        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
#                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                    key, _ = get_numbered_name(itemlist[0], nitem, looker, key=key)
                    if itemlist[0].db.ardēns:
                        key = "|y(ardēns)|n " + key
                    if itemlist[0].db.descriptive_name:
                        key = itemlist[0].db.descriptive_name
                else:
#                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                    key = [get_numbered_name(item, nitem, looker, key=key)[1] for item in itemlist][
                        0
                    ]
                thing_strings.append(key)

            string += "\n|wEcce:|n\n " + list_to_string(users + thing_strings)

        return string


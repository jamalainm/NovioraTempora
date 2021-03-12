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

from evennia.utils import ansi

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

                populate_forms(self, nominative, genitive, sexus)

                # Check if there is a nōmen for this character
                if len(self.db.formae['nom_sg']) > 1:

                    populate_forms(self, nōmen_nom, nōmen_gen, sexus)

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
        # adjusted the exit name to take out the dbref so builders can
        # click on the exits to go there
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(con.key)
            elif con.has_account:
                if con.db.ardēns:
                    users.append("|y(ardēns)|n |c%s|n" % key)
                else:
                    users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)

        # get description, build string
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        # JI (12/7/9) Adding the following lines to accommodate clothing
        # Actually, added return_appearance to characters typeclass
        # and commenting this new section out
#        worn_string_list = []
#        clothes_list = get_worn_clothes(self, exclude_covered=True)
#        # Append worn, uncovered clothing to the description
#        for garment in clothes_list:
#            # if 'worn' is True, just append the name
#            if garment.db.worn is True:
#                # JI (12/7/19) append the accusative name to the description,
#                # since these will be direct objects
#                worn_string_list.append(garment.db.acc_sg)
#            # Otherwise, append the name and the string value of 'worn'
#            elif garment.db.worn:
#                worn_string_list.append("%s %s" % (garment.name, garment.db.worn))
        if desc:
            string += "%s" % desc
#        # Append worn clothes.
#        if worn_string_list:
#            string += "|/|/%s gerit: %s." % (self, list_to_string(worn_string_list))
#        else:
#            string += "|/|/%s nud%s est!" % (self, 'a' if self.db.gender == 1 else 'us')
#        return string
        # Thinking that the above, added for clothing, might need to only be in the
        # character typeclass
        if exits:
            # Changing this string so that exits appear green
            # string += "\n|wAd hos locos potes ire:|n\n " + LatinNoun.list_to_string(exits)
            colorful_exits = []
            for exit in exits:
                colorful_exits.append(f"|lc{exit}|lt|g{exit}|n|le")
            colorful_exits = sorted(colorful_exits)
            string += "\n|wAd hōs locōs īre licet:|n\n " + list_to_string(colorful_exits)
        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
#                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                    key, _ = get_numbered_name(itemlist[0], nitem, looker, key=key)
                    if itemlist[0].db.is_burning:
                        key = "|y(ardēns)|n " + key
                else:
#                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                    key = [get_numbered_name(item, nitem, looker, key=key)[1] for item in itemlist][
                        0
                    ]
                thing_strings.append(key)

            string += "\n|wEcce:|n\n " + list_to_string(users + thing_strings)

        return string


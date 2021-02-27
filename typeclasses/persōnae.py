"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter

from typeclasses.inflected_noun import InflectedNoun
from utils.latin_language.populate_forms import populate_forms

import random

class Persōna(DefaultCharacter,InflectedNoun):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

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

                self.db.lang = 'latin'

                # assign handedness
                if random.random() >= 0.9:
                    self.db.handedness = 'sinistrā'
                else:
                    self.db.handedness = 'dextrā'

                # Set 'manibus_plēnīs' and 'manibus_vacuīs'
                self.db.manibus_plēnīs = []
                self.db.manibus_vacuīs = ['dextrā','sinistrā']

                # Set stats if not already given
                if not self.db.ingenia:
                    statNums = [0,0,0,0,0,0]
                    points = 27
                    while points > 0:
                        index = random.randint(0,5)
                        if statNums[index] < 5 and points > 0:
                            statNums[index] += 1
                            points -= 1
                        elif statNums[index] in [5, 6] and points > 1:
                            statNums[index] += 1
                            points -= 2
                    for index, value in enumerate(statNums):
                        statNums[index] += 9

                    self.db.ingenia = {'vīrēs':statNums[0], 'pernīcitās':statNums[1],'valētūdō':statNums[2],'ratiō':statNums[3],'sapientia':statNums[4],'grātia':statNums[5]}

                # Set 'puncta valētūdinis' (health points)
                bonus = self.db.ingenia['valētūdō']
                bonus = (bonus - 11) if bonus % 2 else (bonus - 10)
                max_pv = (10 + bonus) if (10 + bonus) > 0 else 1
                self.db.pv = {'max': max_pv, "nunc": max_pv}

                # Set carrying capacity
                strength = self.db.ingenia['vīrēs']
                self.db.toll_fer = {
                        'tollere': round(strength * 30 * 0.45, 1),
                        'impedīta': round(strength * 5 * 0.45, 1),
                        'impedītissima': round(strength * 10 * 0.45, 1),
                        'ferēns': 0,
                        'max': round(strength * 15 * 0.45, 1)
                        }

            else:
                pass
        else:
            pass

"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom

from utils.latin_language.populate_forms import populate_forms
# from typeclasses.inflected_noun import InflectedNoun

class Locus(DefaultRoom):
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

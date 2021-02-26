# file mygame/typeclasses/latin_noun.py

from evennia import DefaultObject
from utils.latin_language.populate_forms import populate_forms

class InflectedNoun(DefaultObject):
    """
    This is my solution to populating all of the inflected forms of
    Latin nouns on creation
    """

    def basetype_posthook_setup(self):

        # add all of the case endings to attributes
        if hasattr(self, 'db'):
            if self.db.formae:

                nominative = self.db.formae['nom_sg'][0]
                genitive = self.db.formae['gen_sg'][0]
                sexus = self.db.sexus

                populate_forms(self, nominative, genitive, sexus)

            else:
                pass
        else:
            pass


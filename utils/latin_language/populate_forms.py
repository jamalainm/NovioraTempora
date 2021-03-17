# file mygame/utils/latin_language/populate_forms.py

from utils.latin_language.decline_noun import DeclineNoun
from unidecode import unidecode

def populate_forms(self,nom='cīvis',gen='cīvis',gender='muliebre'):
    """
    A helper function for at_object_creation() for Latin typeclasses
    """

    word = DeclineNoun(nom=nom,gen=gen,gender=gender)
    forms = word.make_paradigm()

    for key, value in forms.items():
        if key in self.db.formae:
            if value not in self.db.formae[key]:
                self.db.formae[key].append(value)
        else:
            self.db.formae.update({key: [value]})

    for form in forms.values():
        self.aliases.add(form)
        self.aliases.add(unidecode(form))

# file mygame/utils/sample_char.py

from evennia.utils import create
from typeclasses.locī import Locus
from typeclasses.rēs import Rēs
from typeclasses.persōnae import Persōna

def sample_obj(self,obj,nom,gen,gender):
    """ Loads sample traits onto a character """
    self.obj, errors = Rēs.create(
            key = nom,
            location = self.room1,
            home = self.room1,
            attributes = [
                ('sexus',gender),
                ('formae', {'nom_sg': [nom], 'gen_sg': [gen]}),
                ('physical',{
                    'māteria': 'ferrum',
                    'rigēns': True,
                    'litra': 0.08,
                    'x': 0.04,
                    'y': 0.65,
                    'z': 0.003,
                    'massa': 0.6
                    }
                    )
                ]
            )

def sample_char(self,char,nom_pair,gen_pair,gender):
    """
    Submit the variable name, nominative pair, genitive pair, and gender
    """

    self.char, errors = Persōna.create(
            key = nom_pair[0] + ' ' + nom_pair[1],
            location = self.room1,
            home = self.room1,
            attributes=[
                ('formae',{'nom_sg': [nom_pair[0],nom_pair[1]],'gen_sg': [gen_pair[0],gen_pair[1]]}),
                ('sexus',gender),
                ('nōmen',nom_pair[1]),
                ('praenōmen',nom_pair[0]),
                ('gens',nom_pair[1]),
                ])

def sample_room(self,room,nom,gen,gender):
    self.room, errors = Locus.create(
            key = nom,
            nohome = True,
            attributes=[
                ('formae',{'nom_sg': [nom], 'gen_sg': [gen]}),
                ('sexus', gender)
                ]
            )


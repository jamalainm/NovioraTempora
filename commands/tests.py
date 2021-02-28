# file mygame/commands/tests.py
from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import LocalEvenniaTest
from evennia.utils import create

from utils.sample_objs import sample_obj, sample_char, sample_room
from typeclasses.persōnae import Persōna
from typeclasses.rēs import Rēs
from typeclasses.locī import Locus

from commands.iussa import *

class ItemEncumbranceTestCase(CommandTest):
    """ Test case for at_get / at_drop hooks. """

    character_typeclass = Persōna
    object_typeclass = Rēs
    room_typeclass = Locus

    def setUp(self):
        super(ItemEncumbranceTestCase, self).setUp()
        # Set up sample room
        self.room1, errors = Locus.create(key="Room", nohome=True,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['cubiculum'], 'gen_sg': ['cubiculī']}),
                ('sexus', 'neutrum'),
                ],
            )
        self.room1.db.desc = "room_desc"

        # Set up sample objects
        self.obj1 = create.create_object(
            typeclass=Rēs, key="gladius", location=self.room1, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['gladius'], 'gen_sg': ['gladiī']}),
                ('sexus', 'māre'),
                ('latin',True),
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

        self.obj2, errors = Rēs.create(
            key="vacca", location=self.room1, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['vacca'], 'gen_sg': ['vaccae']}),
                ('latin',True),
                ('sexus', 'muliebre'),
                ('physical',{
                    'māteria': 'carō',
                    'rigēns': False,
                    'litra': 100,
                    'x': 2.6,
                    'y': 1.8,
                    'z': 0.8,
                    'massa': 907
                    }
                    )
                ]
        )

        # Set up sample character
        self.char1, errors = Persōna.create(
            "Gaia Iūlia", home=self.room1, location=self.room1,
            attributes=[
                ('formae',{'nom_sg': ['Gaia','Iūlia'],'gen_sg': ['Gaiae','Iūliae']}),
                ('sexus','muliebre'),
                ('nōmen','Iūlia'),
                ('gens','Iūlia'),
                ('latin',True),
                ('praenōmen','Gaia'),
                ])


    def test_cape(self):
        """ test that cape get hook properly affects encumbrance """
        self.assertEqual(self.char1.db.toll_fer['ferēns'], 0)
        self.call(Cape(), self.obj1.db.formae['acc_sg'][0], f"{self.obj1.db.formae['acc_sg'][0]} cēpistī.|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")
        self.assertEqual(self.char1.db.toll_fer['ferēns'],self.obj1.db.physical['massa'])



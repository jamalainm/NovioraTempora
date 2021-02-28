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
            key="lāna", location=self.room1, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['lāna'], 'gen_sg': ['lānae']}),
                ('latin',True),
                ('sexus', 'muliebre'),
                ('physical',{
                    'māteria': 'lāna',
                    'rigēns': False,
                    'litra': 23,
                    'massa': 3
                    }
                    )
                ]
        )

        self.obj3, errors = Rēs.create(
            key="lūmen", location=self.room1, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['lūmen'], 'gen_sg': ['lūminis']}),
                ('latin',True),
                ('sexus', 'neutrum'),
                ('physical',{
                    'māteria': 'argilla',
                    'rigēns': True,
                    'litra': 0.2,
                    'massa': 0.15,
                    'x': 0.05,
                    'y': 0.05,
                    'z': 0.08
                    }
                    )
                ]
        )

        self.obj4, errors = Rēs.create(
            key="focus", location=self.room1, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['focus'], 'gen_sg': ['focī']}),
                ('latin',True),
                ('sexus', 'māre'),
                ('physical',{
                    'māteria': 'marmor',
                    'rigēns': True,
                    'litra': 3140,
                    'massa': 8512,
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


    def test_cape_relinque(self):
        hands = ['sinistrā', 'dextrā']
        hands.remove(self.char1.db.handedness)
        off_hand = hands[0]

        # Ensure that caller can't take themselves
        self.call(Cape(), self.char1.db.formae['acc_sg'][0], "Tū tē capere nōn potes!")

        # start with no encumberance
        self.assertEqual(self.char1.db.toll_fer['ferēns'], 0)

        # Shouldn't be able to pick up this heavy hearth
        self.call(Cape(), self.obj4.db.formae['acc_sg'][0], f"Tantum ponderis ferre nōn potes!|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

        # See if we get the success message for picking something up
        self.call(Cape(), self.obj1.db.formae['acc_sg'][0], f"{self.obj1.db.formae['acc_sg'][0]} cēpistī.|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

        # Ensure the encumberance matches
        self.assertEqual(self.char1.db.toll_fer['ferēns'],self.obj1.db.physical['massa'])

        # Ensure that dominant hand does the picking up
        self.assertIn(self.char1.db.handedness,self.char1.db.manibus_plēnīs)

        # See if we get the success message for picking up a second object
        self.call(Cape(), self.obj2.db.formae['acc_sg'][0], f"{self.obj2.db.formae['acc_sg'][0]} cēpistī.|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

        # Ensure the encumberance accounts for both objects
        self.assertEqual(self.char1.db.toll_fer['ferēns'],self.obj1.db.physical['massa'] + self.obj2.db.physical['massa'])

        # Make sure full hands = 2
        self.assertIn(off_hand,self.char1.db.manibus_plēnīs)

        # Make sure empty hands = 0
        self.assertEqual(len(self.char1.db.manibus_vacuīs),0)

        # Make sure something can't be picked up with both hands full
        self.call(Cape(), self.obj3.db.formae['acc_sg'][0], "Manūs tuae sunt plēnae!")

        # See if we get success message for dropping something
        self.call(Relinque(), self.obj1.db.formae['acc_sg'][0], f"{self.obj1.db.formae['acc_sg'][0]} relīquistī.|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

        # Check that the encumberance has been updated
        self.assertEqual(self.char1.db.toll_fer['ferēns'],self.obj2.db.physical['massa'])

        # Make sure that the hand holding the object has been freed up
        self.assertIn(self.char1.db.handedness,self.char1.db.manibus_vacuīs)
        self.assertEqual(len(self.char1.db.manibus_plēnīs),1)
        self.assertEqual(len(self.char1.db.manibus_vacuīs),1)
        self.assertIn(off_hand,self.char1.db.manibus_plēnīs)

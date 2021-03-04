# file mygame/commands/tests.py
from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import LocalEvenniaTest
from evennia.utils import create

from utils.sample_objs import sample_obj, sample_char, sample_room
from typeclasses.persōnae import Persōna
from typeclasses.rēs import Rēs
from typeclasses.locī import Locus
from typeclasses.vestīmenta import Vestīmentum

from commands.iussa import *

class IndueExueTestCase(CommandTest):

    """ Test case for 'indue' (wear) and 'exue' (take off) """

    character_typeclass = Persōna
    object_typeclass = Vestīmentum

    def setUp(self):
        super(IndueExueTestCase, self).setUp()
        # Set up sample character 1
        self.char1, errors = Persōna.create(
            "Gaia Iūlia", home=self.room1, location=self.room1.dbref,
            attributes=[
                ('formae',{'nom_sg': ['Gaia','Iūlia'],'gen_sg': ['Gaiae','Iūliae']}),
                ('sexus','muliebre'),
                ('nōmen','Iūlia'),
                ('gens','Iūlia'),
                ('latin',True),
                ('praenōmen','Gaia'),
                ])

        self.obj1, errors = Rēs.create(
                "pallium", home=self.room1, locations=self.char1,
                attributes=[
                    ('formae',{'nom_sg': ['pallium'],'gen_sg': ['palliī']}),
                    ('sexus','neutrum'),
                    ('latin',True),
                    ('genusVestīmentōrum','cloak'),
                    ('physical',{'massa':3}),
                    ]
                )

        self.char1.db.toll_fer['ferēns'] = self.obj1.db.physical['massa']
        self.obj.db.tenēutr = self.char1.db.handedness
        self.char1.db.manibus_plēnīs.append(self.char1.db.handedness)
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)

        def test_indue(self):

            # Ensure we get the right message
            self.call(Indue(), self.obj1.db.formae['acc_sg'],f'|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 

            # make sure that held item is out of hands
            assertFalse(self.obj1.db.tenētur)
            assertTrue(self.obj1.db.geritur)
            assertIn(self.char1.db.handedness,self.char1.db.manibus_vacuīs)
            assertEqual(len(self.char1.db.manibus_plēnīs),0)
            assertEqual(self.char1.db.toll_fer['ferēns'],self.obj1.db.physical['massa'])

            # make sure that after taking something off it's in hands
            assertEqual(self.obj1.db.tenētur,self.char1.db.handedness)
            assertFalse(self.obj1.db.geritur)
            assertIn(self.char1.db.handedness,self.char1.db.manibus_plēnīs)
            assertEqual(len(self.char1.db.manibus_vacuīs),0)
            assertEqual(self.char1.db.toll_fer['ferēns'],self.obj1.db.physical['massa'])

class DīcTestCase(CommandTest):
    """ Test case for 'dīc' (say) """

    character_typeclass = Persōna

    def setUp(self):
        super(DīcTestCase, self).setUp()
        # Set up sample character 1
        self.char1, errors = Persōna.create(
            "Gaia Iūlia", home=self.room1, location=self.room1.dbref,
            attributes=[
                ('formae',{'nom_sg': ['Gaia','Iūlia'],'gen_sg': ['Gaiae','Iūliae']}),
                ('sexus','muliebre'),
                ('nōmen','Iūlia'),
                ('gens','Iūlia'),
                ('latin',True),
                ('praenōmen','Gaia'),
                ])

        # Set up sample character 2
        self.char2, errors = Persōna.create(
            "Marcus Appius", home=self.room1, location=self.room1.dbref,
            attributes=[
                ('formae',{'nom_sg': ['Marcus','Appius'],'gen_sg': ['Marcī','Appiī']}),
                ('sexus','māre'),
                ('nōmen','Appius'),
                ('gens','Appia'),
                ('latin',True),
                ('praenōmen','Marcus'),
                ])

    def test_dīc(self):
        """ Set char1 up with an object to drop """

        # See if we get success message for a multi-word phrase
        self.call(Dīc(), "Salvēte amīcī, quid agitis?", f'"Salvēte" inquis "amīcī, quid agitis?"|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})')

        # See if we get success message for a single-word phrase
        self.call(Dīc(), "Salvēte!", f'"Salvēte!" inquis.|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})')

class GettingDroppingGivingTestCase(CommandTest):
    """ Test case for 'cape' (get), 'relinque' (drop), 'da' (give). """

    character_typeclass = Persōna
    object_typeclass = Rēs
    room_typeclass = Locus

    def setUp(self):
        super(GettingDroppingGivingTestCase, self).setUp()
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
            typeclass=Rēs, key="gladius", location=self.room1.dbref, home=self.room1,
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
            key="lāna", location=self.room1.dbref, home=self.room1,
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
            key="lūmen", location=self.room1.dbref, home=self.room1,
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
            key="focus", location=self.room1.dbref, home=self.room1,
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

        # Set up sample character 1
        self.char1, errors = Persōna.create(
            "Gaia Iūlia", home=self.room1, location=self.room1.dbref,
            attributes=[
                ('formae',{'nom_sg': ['Gaia','Iūlia'],'gen_sg': ['Gaiae','Iūliae']}),
                ('sexus','muliebre'),
                ('nōmen','Iūlia'),
                ('gens','Iūlia'),
                ('latin',True),
                ('praenōmen','Gaia'),
                ])

        # Set up sample character 2
        self.char2, errors = Persōna.create(
            "Marcus Appius", home=self.room1, location=self.room1.dbref,
            attributes=[
                ('formae',{'nom_sg': ['Marcus','Appius'],'gen_sg': ['Marcī','Appiī']}),
                ('sexus','māre'),
                ('nōmen','Appius'),
                ('gens','Appia'),
                ('latin',True),
                ('praenōmen','Marcus'),
                ])

    def test_relinque(self):
        """ Set char1 up with an object to drop """
        self.char1.db.location = self.room1.dbref
        self.obj1.location = self.char1
        self.obj1.db.tenētur = self.char1.db.handedness
        self.char1.db.manibus_plēnīs.append(self.char1.db.handedness)
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)
        char1_off_hand = self.char1.db.manibus_vacuīs[0]

        # Establish encumberence
        self.char1.db.toll_fer['ferēns'] = self.obj1.db.physical['massa']

        self.call(Relinque(), self.obj1.db.formae['acc_sg'][0], f"{self.obj1.db.formae['acc_sg'][0]} relīquistī.|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

        self.assertEqual(self.obj1.location, self.char1.location)

        self.assertEqual(self.char1.db.toll_fer['ferēns'], 0)


    def test_simple_da(self):
        """ Set characters in same place, char1 w/ full hands, char2 w/ 1 obj """
        self.char1.db.location = self.room1.dbref
        self.obj1.location = self.char1
        self.obj1.db.tenētur = self.char1.db.handedness
        self.char1.db.manibus_plēnīs.append(self.char1.db.handedness)
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)
        char1_off_hand = self.char1.db.manibus_vacuīs[0]
        self.obj2.location = self.char1
        self.obj2.tenētur = char1_off_hand
        self.char1.db.manibus_plēnīs.append(char1_off_hand)
        self.char1.db.manibus_vacuīs.remove(char1_off_hand)

        self.char2.db.location = self.room1.dbref
        self.obj3.location = self.char2
        self.obj3.tenētur = self.char2.db.handedness
        self.char2.db.manibus_plēnīs.append(self.char2.db.handedness)
        self.char2.db.manibus_vacuīs.remove(self.char2.db.handedness)
        char2_off_hand = self.char2.db.manibus_vacuīs[0]

        # Establish base encumberance
        self.char1.db.toll_fer['ferēns'] = self.obj1.db.physical['massa'] + self.obj2.db.physical['massa']
        self.assertEqual(self.char1.db.toll_fer['ferēns'], self.obj1.db.physical['massa'] + self.obj2.db.physical['massa'])
        self.char2.db.toll_fer['ferēns'] = self.obj3.db.physical['massa']
        self.assertEqual(self.char2.db.toll_fer['ferēns'], self.obj3.db.physical['massa'])

        # Check that we get the success message
        self.call(Da(), f"{self.obj1.db.formae['acc_sg'][0]} {self.char2.db.formae['dat_sg'][0]}", f"{self.obj1.db.formae['acc_sg'][0]} {self.char2.db.formae['dat_sg'][0]} dedistī.|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")
        # Check that locations have changed
        self.assertEqual(self.obj1.location, self.char2)

        # Check that encumberance has switched
        self.assertEqual(self.char2.db.toll_fer['ferēns'], self.obj1.db.physical['massa'] + self.obj3.db.physical['massa'])
        self.assertEqual(self.char1.db.toll_fer['ferēns'], self.obj2.db.physical['massa'])

        # Check that hands have been freed up and occupied
        self.assertIn(self.char2.db.handedness, self.char2.db.manibus_plēnīs)
        self.assertEqual(len(self.char2.db.manibus_vacuīs), 0)
        self.assertEqual(len(self.char1.db.manibus_vacuīs), 1)
        self.assertEqual(len(self.char1.db.manibus_plēnīs), 1)

        # Make sure you can't give something to someone whose hands are full
        self.call(Da(), f"{self.obj2.db.formae['acc_sg'][0]} {self.char2.db.formae['dat_sg'][0]}", f"Manūs {self.char2.db.formae['gen_sg'][0]} sunt plēnae!|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

    def test_cape_relinque(self):
        hands = ['sinistrā', 'dextrā']
        hands.remove(self.char1.db.handedness)
        off_hand = hands[0]

        # Ensure that caller can't take themselves
        self.call(Cape(), f"{self.char1.db.formae['acc_sg'][0]}", "Tū tē capere nōn potes!")

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

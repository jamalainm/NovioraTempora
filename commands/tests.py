# file mygame/commands/tests.py
from evennia.commands.default.tests import CommandTest
from evennia.utils.test_resources import LocalEvenniaTest
from evennia.utils import create

from utils.sample_objs import sample_obj, sample_char, sample_room
from utils.latin_language.adjective_agreement import us_a_um

from typeclasses.persōnae import Persōna
from typeclasses.rēs import Rēs
from typeclasses.locī import Locus
from typeclasses.vestīmenta import Vestīmentum
from typeclasses.exitūs import Exitus

from commands.iussa import *
from commands.vestīre import *

class PōneExcipeTestCase(CommandTest):
    """ Test case for 'pōne' (put) """

    character_typeclass = Persōna
    room_typeclass = Locus
    object_typeclass = Rēs

    def setUp(self):
        super(PōneExcipeTestCase, self).setUp()

        # Set up sample room 1
        self.room1, errors = Locus.create(key="Ātrium", nohome=True,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['ātrium'], 'gen_sg': ['ātriī']}),
                ('sexus', 'neutrum'),
                ],
            )
        self.room1.db.desc = "Hic locus est media domus."

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
                ('desc','Fēmina fortis est.'),
                ])

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

        self.obj2 = create.create_object(
            typeclass=Rēs, key="saccus", location=self.room1.dbref, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['saccus'], 'gen_sg': ['saccī']}),
                ('sexus', 'māre'),
                ('latin',True),
                ('physical',{
                    'māteria': 'linen',
                    'rigēns': False,
                    'litra': 0.75,
                    'massa': 0.45,
                    }
                    ),
                ('capax',{'max_vol':24,'rem_vol':24,"x":0.3,"y":0.4,"z":0.2}),
                ]
            )

        self.obj3, errors = Rēs.create(
            key="lāna", location=self.room1.dbref, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['lāna'], 'gen_sg': ['lānae']}),
                ('latin',True),
                ('sexus', 'muliebre'),
                ('physical',{
                    'māteria': 'lāna',
                    'rigēns': False,
                    'litra': 40,
                    'massa': 3
                    }
                    )
                ]
            )

        # Set up sample objects
        self.obj4 = create.create_object(
            typeclass=Rēs, key="hasta", location=self.room1.dbref, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['hasta'], 'gen_sg': ['hastae']}),
                ('sexus', 'muliebre'),
                ('latin',True),
                ('physical',{
                    'māteria': 'ferrum',
                    'rigēns': True,
                    'litra': 0.08,
                    'x': 0.04,
                    'y': 2.00,
                    'z': 0.003,
                    'massa': 0.6
                    }
                    )
                ]
            )

        self.obj5 = create.create_object(
            typeclass=Rēs, key="arca", location=self.room1.dbref, home=self.room1,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['arca'], 'gen_sg': ['arcae']}),
                ('sexus', 'muliebre'),
                ('latin',True),
                ('physical',{
                    'māteria': 'lignea',
                    'rigēns': True,
                    'litra': 0.75,
                    'massa': 0.45,
                    }
                    ),
                ('capax',{'max_vol':24,'rem_vol':24,"x":1,"y":0.5,"z":0.5}),
                ]
            )

    def test_excipe_external(self):
        """ Set up external container with object for char1 to get """
        self.char1.db.location = self.room1.dbref
        self.obj5.location = self.room1.dbref
        self.obj1.location = self.obj5

        self.call(Excipe(),
                f"{self.obj1.db.formae['acc_sg'][0]} ex {self.obj5.db.formae['abl_sg'][0]}",
                f"{self.obj1.db.formae['acc_sg'][0]} ex" +
                f" {self.obj5.db.formae['abl_sg'][0]}" +
                f" cēpistī." +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})"
                )

        self.assertEqual(self.char1.db.toll_fer['ferēns'],self.obj1.db.physical['massa'])
        self.assertEqual(self.char1.db.manibus_plēnīs[0],self.char1.db.handedness)

    def test_excipe_held_container(self):
        """ Set up held container with object for char1 to get """
        self.char1.db.location = self.room1.dbref
        self.obj2.location = self.char1
        self.obj1.location = self.obj2
        self.obj2.db.tenētur = self.char1.db.handedness
        self.char1.db.manibus_plēnīs.append(self.char1.db.handedness)
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)
        self.char1.db.toll_fer['ferēns'] = self.obj1.db.physical['massa'] + self.obj2.db.physical['massa']

        self.call(Excipe(),
                f"{self.obj1.db.formae['acc_sg'][0]} ex {self.obj2.db.formae['abl_sg'][0]}",
                f"{self.obj1.db.formae['acc_sg'][0]} ex" +
                f" {self.obj2.db.formae['abl_sg'][0]}" +
                f" cēpistī." +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})"
                )

        self.assertEqual(self.char1.db.toll_fer['ferēns'],self.obj1.db.physical['massa'] + self.obj2.db.physical['massa'])
        self.assertEqual(len(self.char1.db.manibus_plēnīs),2)
        self.assertEqual(len(self.char1.db.manibus_vacuīs),0)
        self.assertEqual(self.obj1.location,self.char1)
        self.assertTrue(self.obj1.db.tenētur)

    def test_pōne_target_too_long(self):
        """ Set char1 up with an object to place in sack """
        self.char1.db.location = self.room1.dbref
        self.obj4.location = self.char1
        self.obj4.db.tenētur = self.char1.db.handedness
        self.char1.db.manibus_plēnīs.append(self.char1.db.handedness)
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)
        char1_off_hand = self.char1.db.manibus_vacuīs[0]

        self.obj2.location = self.char1
        self.obj2.tenētur = char1_off_hand
        self.char1.db.manibus_plēnīs.append(char1_off_hand)
        self.char1.db.manibus_vacuīs.remove(char1_off_hand)

        # Establish encumberence
        self.char1.db.toll_fer['ferēns'] = self.obj4.db.physical['massa'] + self.obj2.db.physical['massa']

        self.call(Pōne(), 
                f"{self.obj4.db.formae['acc_sg'][0]} in {self.obj2.db.formae['acc_sg'][0]}", 
                f"{self.obj2.name} satis altus nōn est!" +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

    def test_pōne_inadquate_space(self):
        """ Set char1 up with an object to place in sack """
        self.char1.db.location = self.room1.dbref
        self.obj3.location = self.char1
        self.obj3.db.tenētur = self.char1.db.handedness
        self.char1.db.manibus_plēnīs.append(self.char1.db.handedness)
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)
        char1_off_hand = self.char1.db.manibus_vacuīs[0]

        self.obj2.location = self.char1
        self.obj2.tenētur = char1_off_hand
        self.char1.db.manibus_plēnīs.append(char1_off_hand)
        self.char1.db.manibus_vacuīs.remove(char1_off_hand)

        # Establish encumberence
        self.char1.db.toll_fer['ferēns'] = self.obj3.db.physical['massa'] + self.obj2.db.physical['massa']

        self.call(Pōne(), 
                f"{self.obj3.db.formae['acc_sg'][0]} in {self.obj2.db.formae['acc_sg'][0]}", 
                f"Magnitūdō {self.obj3.db.formae['gen_sg'][0]} est māior quam spatium in {self.obj2.db.formae['abl_sg'][0]}." +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

    def test_pōne_fits(self):
        """ Set char1 up with an object to place in sack """
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

        # Establish encumberence
        self.char1.db.toll_fer['ferēns'] = self.obj1.db.physical['massa'] + self.obj2.db.physical['massa']

        self.call(Pōne(), 
                f"{self.obj1.db.formae['acc_sg'][0]} in {self.obj2.db.formae['acc_sg'][0]}", 
                f"{self.obj1.db.formae['acc_sg'][0]}" +
                f" in {self.obj2.db.formae['acc_sg'][0]} posuistī." + 
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

        # Make sure target location has changed
        self.assertEqual(self.obj1.location,self.obj2)
        # Make sure hands are freed up
        self.assertEqual(self.char1.db.manibus_vacuīs[0],self.char1.db.handedness)
        self.assertEqual(self.char1.db.manibus_plēnīs[0],char1_off_hand)
        # Make sure target is no longer held
        self.assertFalse(self.obj1.db.tenētur)

    def test_pōne_external_container(self):
        """ Set char1 up with an object to place in sack """
        self.char1.db.location = self.room1.dbref
        self.obj1.location = self.char1
        self.obj1.db.tenētur = self.char1.db.handedness
        self.char1.db.manibus_plēnīs.append(self.char1.db.handedness)
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)
        char1_off_hand = self.char1.db.manibus_vacuīs[0]

        self.obj5.location = self.room1.dbref

        # Establish encumberence
        self.char1.db.toll_fer['ferēns'] = self.obj1.db.physical['massa']

        self.call(Pōne(), 
                f"{self.obj1.db.formae['acc_sg'][0]} in {self.obj5.db.formae['acc_sg'][0]}", 
                f"{self.obj1.db.formae['acc_sg'][0]}" +
                f" in {self.obj5.db.formae['acc_sg'][0]} posuistī." + 
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']})")

        # Make sure target location has changed
        self.assertEqual(self.obj1.location,self.obj5)
        # Make sure hands are freed up
        self.assertEqual(len(self.char1.db.manibus_vacuīs),2)
        self.assertEqual(len(self.char1.db.manibus_plēnīs),0)
        # Make sure target is no longer held
        self.assertFalse(self.obj1.db.tenētur)
        # Make sure mass of target no part of encumberance
        self.assertEqual(self.char1.db.toll_fer['ferēns'],0)

class SpectāTestCase(CommandTest):
    """ Test case for 'spectā' (behold) """

    character_typeclass = Persōna
    room_typeclass = Locus
    object_typeclass = Rēs
    exit_typeclass = Exitus

    def setUp(self):
        super(SpectāTestCase, self).setUp()

        # Set up sample room 1
        self.room1, errors = Locus.create(key="Ātrium", nohome=True,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['ātrium'], 'gen_sg': ['ātriī']}),
                ('sexus', 'neutrum'),
                ],
            )
        self.room1.db.desc = "Hic locus est media domus."

        # Set up sample room 2
        self.room2, errors = Locus.create(key="Cubiculum", nohome=True,
            # adding this for unit testing of Latin
            attributes=[
                ('formae', {'nom_sg': ['cubiculum'], 'gen_sg': ['cubiculī']}),
                ('sexus', 'neutrum'),
                ],
            )
        self.room2.db.desc = "Hic locus est ad dormiendum idoneus."

        # Set up sample exit from room 1 to room 2
        self.exit1, errors = Exitus.create(
                "in cubiculum",
                self.room1,
                self.room2,
                description="Haec ianua in cubiculum dūcit.",
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
                ('desc','Fēmina fortis est.'),
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
                ('desc','Vir fortis est.'),
                ])

        # Set up clothes for a character to wear when looked at
        self.obj1, errors = Vestīmentum.create(
                "pallium", home=self.room1,
                attributes=[
                    ('formae',{'nom_sg': ['pallium'],'gen_sg': ['palliī']}),
                    ('sexus','neutrum'),
                    ('latin',True),
                    ('genusVestīmentōrum','cloak'),
                    ('physical',{'massa':3}),
                    ('desc','A dashing cloak'),
                    ]
                )

        self.obj2, errors = Vestīmentum.create(
                "petasus", home=self.room1,
                attributes=[
                    ('formae',{'nom_sg': ['petasus'],'gen_sg': ['petasī']}),
                    ('sexus','māre'),
                    ('latin',True),
                    ('genus_Vestīmentōrum','hat'),
                    ('physical',{'massa':3}),
                    ('desc','A cunning, wide-brimmed hat'),
                    ]
                )

        self.obj3, errors = Vestīmentum.create(
                "soleae", home=self.room1,
                attributes=[
                    ('formae',{'nom_sg': ['soleae'],'gen_sg': ['soleārum']}),
                    ('sexus','muliebre'),
                    ('latin',True),
                    ('genus_Vestīmentōrum','shoes'),
                    ('physical',{'massa':3}),
                    ('desc','Simple sandals'),
                    ]
                )

        self.obj4, errors = Vestīmentum.create(
                "petasus", home=self.room1,
                attributes=[
                    ('formae',{'nom_sg': ['petasus'],'gen_sg': ['petasī']}),
                    ('sexus','māre'),
                    ('latin',True),
                    ('genus_Vestīmentōrum','hat'),
                    ('physical',{'massa':3}),
                    ('desc','A cunning, wide-brimmed hat'),
                    ]
                )


    def test_spectā_no_target_empty_room(self):
        self.char1.location = self.room1.dbref
        self.char2.location = self.room2.dbref
        self.obj1.location = self.char2
        self.obj2.location = self.char2
        self.obj3.location = self.char2

        self.call(Spectā(),'', f"{self.room1.key}" + '\n' + f"{self.room1.db.desc}" + '\n' + "Ad hōs locōs īre licet:" + '\n' + f" {self.exit1.key}|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) ")

    def test_spectā_no_target_things_in_room(self):
        self.char1.location = self.room1.dbref
        self.char2.location = self.room1.dbref
        self.obj1.location = self.room1.dbref
        self.obj2.location = self.room1.dbref
        self.obj3.location = self.char2
        self.obj4.location = self.room1.dbref

        self.call(Spectā(),'', f"{self.room1.key}" + '\n' + 
                f"{self.room1.db.desc}" + '\n' + 
                "Ad hōs locōs īre licet:" + '\n' + 
                f" {self.exit1.key}" + '\n' +
                "Ecce:" + '\n' +
                f" {self.char2.key}, {self.obj1.db.formae['nom_sg'][0]}" +
                f" et 2 {self.obj4.db.formae['nom_pl'][0]}"
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

    def test_spectā_no_target_2_same_thing_in_room(self):
        self.char1.location = self.room1.dbref
        self.char2.location = self.room1.dbref
        self.obj1.location = self.room1.dbref
        self.obj2.location = self.char2
        self.obj3.location = self.char2

        self.call(Spectā(),'', f"{self.room1.key}" + '\n' + 
                f"{self.room1.db.desc}" + '\n' + 
                "Ad hōs locōs īre licet:" + '\n' + 
                f" {self.exit1.key}" + '\n' +
                "Ecce:" + '\n' +
                f" {self.char2.key} et {self.obj1.db.formae['nom_sg'][0]}" +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

    def test_spectā_targeting_object(self):
        self.char1.location = self.room1.dbref
        self.obj1.location = self.room1.dbref

        self.call(Spectā(), self.obj1.db.formae['acc_sg'][0], f"{self.obj1.key}" + '\n' +
                f"{self.obj1.db.desc}" +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

    def test_spectā_targeting_naked_character(self):
        self.char1.location = self.room1.dbref
        self.char2.location = self.room1.dbref

        # Grammatically masculine target
        self.call(Spectā(), self.char2.db.formae['acc_sg'][0], f"{self.char2.get_display_name(self.char1)}" + '\n' +
                f"{self.char2.db.desc}" + '\n' +
                '\n' +
                f"{self.char2.key} nūdus est!" +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

        # Grammatically masculine target
        self.call(Spectā(), self.char1.db.formae['acc_sg'][0], f"{self.char1.get_display_name(self.char1)}" + '\n' +
                f"{self.char1.db.desc}" + '\n' +
                '\n' +
                f"{self.char1.key} nūda est!" +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

    def test_spectā_targeting_character_holding_something(self):
        self.char1.location = self.room1.dbref
        self.char2.location = self.room1.dbref
        self.obj1.location = self.char2
        self.obj1.db.tenētur = self.char2.db.handedness

        # Grammatically masculine target
        self.call(Spectā(), self.char2.db.formae['acc_sg'][0], f"{self.char2.get_display_name(self.char1)}" + '\n' +
                f"{self.char2.db.desc}" + '\n' +
                '\n' +
                f"tenet: pallium.\n\n" 
                f"{self.char2.key} nūdus est!" +
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

    def test_spectā_targeting_character_wearing_something(self):
        self.char1.location = self.room1.dbref
        self.char2.location = self.room1.dbref
        self.obj1.location = self.char2
        self.obj1.db.geritur = True

        # Grammatically masculine target
        self.call(Spectā(), self.char2.db.formae['acc_sg'][0], f"{self.char2.get_display_name(self.char1)}" + '\n' +
                f"{self.char2.db.desc}" + '\n' +
                '\n' +
                f"gerit: pallium." 
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

    def test_spectā_targeting_character_wearing_and_holding_something(self):
        self.char1.location = self.room1.dbref
        self.char2.location = self.room1.dbref
        self.obj1.location = self.char2
        self.obj1.db.geritur = True
        self.obj2.location = self.char2
        self.obj2.db.tenētur = self.char2.db.handedness

        # Try looking at someone wearing and holding something
        self.call(Spectā(), self.char2.db.formae['acc_sg'][0], f"{self.char2.get_display_name(self.char1)}" + '\n' +
                f"{self.char2.db.desc}" + '\n' +
                '\n' +
                f"tenet: petasum.\n\n" +
                f"gerit: pallium." 
                f"|Vīta: {self.char1.db.pv['nunc']}/{self.char1.db.pv['max']}) "
                )

class DīcTestCase(CommandTest):
    """ Test case for 'dīc' (say) """

    character_typeclass = Persōna
    room_typeclass = Locus

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
        # Explicitly puppet a character; dealing with problems after introducing EventChar
        self.account.puppet_object(self.session, self.char1)

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

class IndueExueTestCase(CommandTest):
    """ Test case for 'indue' (wear) and 'exue' (take off) """

    character_typeclass = Persōna
    object_typeclass = Vestīmentum
    room_typeclass = Locus

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

        self.obj1, errors = Vestīmentum.create(
                "pallium", home=self.room1,
                attributes=[
                    ('formae',{'nom_sg': ['pallium'],'gen_sg': ['palliī']}),
                    ('sexus','neutrum'),
                    ('latin',True),
                    ('genusVestīmentōrum','cloak'),
                    ('physical',{'massa':3}),
                    ]
                )

        self.obj2, errors = Vestīmentum.create(
                "petasus", home=self.room1,
                attributes=[
                    ('formae',{'nom_sg': ['petasus'],'gen_sg': ['petasī']}),
                    ('sexus','māre'),
                    ('latin',True),
                    ('genus_Vestīmentōrum','hat'),
                    ('physical',{'massa':3}),
                    ]
                )

        self.obj3, errors = Vestīmentum.create(
                "soleae", home=self.room1,
                attributes=[
                    ('formae',{'nom_sg': ['soleae'],'gen_sg': ['soleārum']}),
                    ('sexus','muliebre'),
                    ('latin',True),
                    ('genus_Vestīmentōrum','shoes'),
                    ('physical',{'massa':3}),
                    ]
                )


    def test_indue(self):
        """ Put on an article of clothing that is held and take off one worn """
        # set up objects
        self.obj1.location = self.char1
        self.obj1.db.tenētur = self.char1.db.handedness
        self.char1.db.manibus_plēnīs = [self.char1.db.handedness]
        self.char1.db.manibus_vacuīs.remove(self.char1.db.handedness)
        off_hand = self.char1.db.manibus_vacuīs[0]
    

        self.obj2.location = self.char1
        self.obj2.db.tenētur = off_hand
        self.char1.db.manibus_plēnīs.append(off_hand)
        self.char1.db.manibus_vacuīs = []

        self.obj3.location = self.char1
        self.obj3.db.geritur = True

        mass_carried = self.obj1.db.physical['massa'] + self.obj2.db.physical['massa'] + self.obj3.db.physical['massa']

        self.char1.db.toll_fer['ferēns'] = mass_carried

        # Ensure we get the right message
        self.call(Indue(), self.obj1.db.formae['acc_sg'][0],f'{self.obj1.db.formae["acc_sg"][0]} induistī.|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 

        # make sure that held item is out of hands
        self.assertFalse(self.obj1.db.tenētur)
        self.assertTrue(self.obj1.db.geritur)
        self.assertIn(self.char1.db.handedness,self.char1.db.manibus_vacuīs)
        self.assertEqual(len(self.char1.db.manibus_plēnīs),1)
        self.assertEqual(self.char1.db.toll_fer['ferēns'],mass_carried)

        """ Take off an article of clothing """
        self.call(Exue(), self.obj1.db.formae['acc_sg'][0],f'{self.obj1.db.formae["acc_sg"][0]} exuistī.|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 

        # make sure that after taking something off it's in hands
        self.assertEqual(self.obj1.db.tenētur,self.char1.db.handedness)
        self.assertFalse(self.obj1.db.geritur)
        self.assertIn(self.char1.db.handedness,self.char1.db.manibus_plēnīs)
        self.assertEqual(len(self.char1.db.manibus_vacuīs),0)
        self.assertEqual(self.char1.db.toll_fer['ferēns'],mass_carried)

        # Make sure that with full hands you can't take something off
        self.call(Exue(), self.obj3.db.formae['acc_sg'][0],f'Manūs tuae sunt plēnae!|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 
        self.assertTrue(self.obj3.db.geritur)
        self.assertEqual(len(self.char1.db.manibus_plēnīs),2)
        self.assertEqual(len(self.char1.db.manibus_vacuīs),0)
        self.assertEqual(self.char1.db.toll_fer['ferēns'],mass_carried)

    def test_relinque_exue(self):
        """ Drop something that is worn """
        self.obj1.location = self.char1
        self.obj1.db.tenētur = 'dextrā'
        self.obj2.location = self.char1
        self.obj2.db.tenētur = 'sinistrā'
        self.obj3.location = self.char1
        self.obj3.db.geritur = True

        self.char1.db.manibus_plēnīs = ['sinistrā','dextrā']
        self.char1.db.manibus_vacuīs = []


        # Can't take off & drop if hands are full
        self.call(Relinque(), self.obj3.db.formae['acc_sg'][0],
                f'Manūs tuae sunt plēnae!|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 

        # Free up one hand
        self.char1.db.manibus_vacuīs.append(self.obj1.db.tenētur)
        self.char1.db.manibus_plēnīs.remove(self.obj1.db.tenētur)
        self.obj1.db.tenētur = False
        self.obj1.location = self.room1

        # Drop something worn
        self.call(Relinque(), self.obj3.db.formae['acc_sg'][0],
                f'{self.obj3.db.formae["acc_sg"][0]} exuistī.|{self.obj3.db.formae["acc_sg"][0]} relīquistī.|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 
    
    def test_da_exue(self):
        """ Give something that is worn """
        self.obj1.location = self.char1
        self.obj1.db.tenētur = 'dextrā'
        self.obj2.location = self.char1
        self.obj2.db.tenētur = 'sinistrā'
        self.obj3.location = self.char1
        self.obj3.db.geritur = True

        self.char1.db.manibus_plēnīs = ['sinistrā','dextrā']
        self.char1.db.manibus_vacuīs = []


        # Can't take off & give if hands are full
        self.call(Da(), f"{self.obj3.db.formae['acc_sg'][0]} {self.char2.db.formae['dat_sg'][0]}",
                f'Manūs tuae sunt plēnae!|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 

        # Free up one hand
        self.char1.db.manibus_vacuīs.append(self.obj1.db.tenētur)
        self.char1.db.manibus_plēnīs.remove(self.obj1.db.tenētur)
        self.obj1.db.tenētur = False
        self.obj1.location = self.room1

        # Drop something worn
        self.call(Da(), f"{self.obj3.db.formae['acc_sg'][0]} {self.char2.db.formae['dat_sg'][0]}",
                f'{self.obj3.db.formae["acc_sg"][0]} exuistī.|{self.obj3.db.formae["acc_sg"][0]} {self.char2.db.formae["dat_sg"][0]} dedistī.|Vīta: {self.char1.db.pv["nunc"]}/{self.char1.db.pv["max"]})') 

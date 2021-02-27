from evennia.utils.test_resources import LocalEvenniaTest, EvenniaTest
from evennia.objects.tests import *
from typeclasses.persōnae import Persōna
from typeclasses.rēs import Rēs
from typeclasses.locī import Locus
from typeclasses.exitūs import Exitus

class DefaultObjectTest(LocalEvenniaTest):

    ip = "212.216.139.14"

    def test_object_create(self):
        description = "A home for a grouch."
        home = self.room1.dbref

        obj, errors = Rēs.create(
                "corbula", 
                self.account, 
                description=description, 
                ip=self.ip, 
                home=home, 
                attributes=[
                    ('formae', {'nom_sg': ['corbula'], 'gen_sg': ['corbulae']},
                        ),
                    ('sexus', 'muliebre'),
                    ]
        )
        self.assertTrue(obj, errors)
        self.assertFalse(errors, errors)
        self.assertEqual(description, obj.db.desc)
        self.assertEqual(obj.db.creator_ip, self.ip)
        self.assertEqual(obj.db_home, self.room1)
        self.assertEqual(obj.db.formae['acc_sg'][0],'corbulam')
        self.assertEqual(obj.db.sexus,'muliebre')

    def test_fem_character_create(self):
        home = self.room1.dbref

        # Feminine Character
        obj_fem, errors = Persōna.create(
            "Gaia Iūlia", self.account, ip=self.ip, home=home,
            attributes=[
                ('formae',{'nom_sg': ['Gaia','Iūlia'],'gen_sg': ['Gaiae','Iūliae']}),
                ('sexus','muliebre'),
                ('nōmen','Iūlia'),
                ('gens','Iūlia'),
                ('praenōmen','Gaia'),
                ])
        self.assertTrue(obj_fem, errors)
        self.assertFalse(errors, errors)
#        self.assertEqual(description, obj.db.desc)
        self.assertEqual(obj_fem.db.creator_ip, self.ip)
        self.assertEqual(obj_fem.db_home, self.room1)
        self.assertEqual(obj_fem.db.formae['acc_sg'][0], 'Gaiam')
        self.assertEqual(obj_fem.db.formae['acc_sg'][1], 'Iūliam')
        self.assertEqual(obj_fem.db.sexus, 'muliebre')
        for i in obj_fem.db.ingenia.values():
            self.assertNotEqual(i,0)
        self.assertTrue(obj_fem.db.handedness)
        self.assertGreater(obj_fem.db.pv['max'],0)
        self.assertGreater(obj_fem.db.pv['nunc'],0)
        self.assertGreater(obj_fem.db.toll_fer['tollere'],0)
        self.assertGreater(obj_fem.db.toll_fer['impedīta'],0)
        self.assertGreater(obj_fem.db.toll_fer['impedītissima'],0)
        self.assertEqual(obj_fem.db.toll_fer['ferēns'],0)
        self.assertGreater(obj_fem.db.toll_fer['max'],0)

    def test_masc_character_create(self):
        home = self.room1.dbref

        # Masculine Character
        obj_masc, errors = Persōna.create(
            "Opiter Cornēlius", self.account, ip=self.ip, home=home,
            attributes=[
                ('formae',{'nom_sg': ['Opiter','Cornēlius'],'gen_sg': ['Opitris','Cornēliī']}),
                ('sexus','māre'),
                ('nōmen','Cornēlius'),
                ('gens','Cornēlia'),
                ('praenōmen','Opiter'),
                ])
        self.assertTrue(obj_masc, errors)
        self.assertFalse(errors, errors)
#        self.assertEqual(description, obj.db.desc)
        self.assertEqual(obj_masc.db.creator_ip, self.ip)
        self.assertEqual(obj_masc.db_home, self.room1)
        self.assertEqual(obj_masc.db.formae['acc_sg'][0], 'Opitrem')
        self.assertEqual(obj_masc.db.formae['acc_sg'][1], 'Cornēlium')
        self.assertEqual(obj_masc.db.sexus, 'māre')
        for i in obj_masc.db.ingenia.values():
            self.assertNotEqual(i,0)
        self.assertTrue(obj_masc.db.handedness)
        self.assertGreater(obj_masc.db.pv['max'],0)
        self.assertGreater(obj_masc.db.pv['nunc'],0)
        self.assertGreater(obj_masc.db.toll_fer['tollere'],0)
        self.assertGreater(obj_masc.db.toll_fer['impedīta'],0)
        self.assertGreater(obj_masc.db.toll_fer['impedītissima'],0)
        self.assertEqual(obj_masc.db.toll_fer['ferēns'],0)
        self.assertGreater(obj_masc.db.toll_fer['max'],0)

    def test_character_create_noaccount(self):
        obj, errors = Persōna.create("oscar", None, home=self.room1.dbref)
        self.assertTrue(obj, errors)
        self.assertFalse(errors, errors)
        self.assertEqual(obj.db_home, self.room1)

    def test_room_create(self):
        description = "A dimly-lit alley behind the local Chinese restaurant."
        obj, errors = Locus.create("alley", self.account, description=description, ip=self.ip)
        self.assertTrue(obj, errors)
        self.assertFalse(errors, errors)
        self.assertEqual(description, obj.db.desc)
        self.assertEqual(obj.db.creator_ip, self.ip)

    def test_exit_create(self):
        description = "The steaming depths of the dumpster, ripe with refuse in various states of decomposition."
        obj, errors = Exitus.create(
            "in", self.room1, self.room2, account=self.account, description=description, ip=self.ip
        )
        self.assertTrue(obj, errors)
        self.assertFalse(errors, errors)
        self.assertEqual(description, obj.db.desc)
        self.assertEqual(obj.db.creator_ip, self.ip)

    def test_urls(self):
        "Make sure objects are returning URLs"
        self.assertTrue(self.char1.get_absolute_url())
        self.assertTrue("admin" in self.char1.web_get_admin_url())

        self.assertTrue(self.room1.get_absolute_url())
        self.assertTrue("admin" in self.room1.web_get_admin_url())

class TestObjectManager(TestObjectManager):

    character_typeclass = Persōna
    object_typeclass = Rēs
    room_typeclass = Locus
    exit_typeclass = Exitus

    
    def test_get_objs_with_key_and_typeclass(self):
        query = ObjectDB.objects.get_objs_with_key_and_typeclass(
            "Char", "typeclasses.persōnae.Persōna"
        )
        self.assertEqual(list(query), [self.char1])
        query = ObjectDB.objects.get_objs_with_key_and_typeclass(
            "Char", "typeclasses.rēs.Rēs"
        )
        self.assertFalse(query)
        query = ObjectDB.objects.get_objs_with_key_and_typeclass(
            "NotFound", "typeclasses.persōnae.Persōna"
        )
        self.assertFalse(query)
        query = ObjectDB.objects.get_objs_with_key_and_typeclass(
            "Char", "typeclasses.persōnae.Persōna", candidates=[self.char1, self.char2]
        )
        self.assertEqual(list(query), [self.char1])

    def test_copy_object(self):
        "Test that all attributes and tags properly copy across objects"

        # Add some tags
        self.obj1.tags.add("plugh", category="adventure")
        self.obj1.tags.add("xyzzy")

        # Add some attributes
        self.obj1.attributes.add("phrase", "plugh", category="adventure")
        self.obj1.attributes.add("phrase", "xyzzy")

        # Create object copy
        obj2 = self.obj1.copy()

        # Make sure each of the tags were replicated
        self.assertTrue("plugh" in obj2.tags.all())
        self.assertTrue("plugh" in obj2.tags.get(category="adventure"))
        self.assertTrue("xyzzy" in obj2.tags.all())

        # Make sure each of the attributes were replicated
        self.assertEqual(obj2.attributes.get(key="phrase"), "xyzzy")
        self.assertEqual(self.obj1.attributes.get(key="phrase", category="adventure"), "plugh")
        self.assertEqual(obj2.attributes.get(key="phrase", category="adventure"), "plugh")

# file mygame/commands/iussa.py
"""
Iussa

Iussa describe the Latin commands and syntax for interacting with the world

"""
from django.conf import settings

from evennia.commands.default import muxcommand
from evennia.utils import create
from evennia import default_cmds
from evennia.objects.models import ObjectDB

from evennia.commands.default.building import ObjManipCommand

from unidecode import unidecode
from random import choice, randint

from utils.latin_language.adjective_agreement import us_a_um
from utils.latin_language.which_one import which_one
from utils.latin_language.check_grammar import check_case
from utils.latin_language.free_hands import free_hands, put_into_hand, take_out_of_hand
from utils.latin_language.gens_class_praenomina import name_data

from typeclasses.locī import Locus
from typeclasses.exitūs import Exitus
from typeclasses.rēs import Ligātūra
# from typeclasses.persōnae import Persōna

class MuxCommand(muxcommand.MuxCommand):
    """
    Eventually we'll want this to display health status after executing
    a command.
    """

    def at_post_cmd(self):
        """
        This hook is called after the command has finished executing
        (after self.func())
        """
        caller = self.caller
        if hasattr(caller, 'db'):
            if caller.db.pv:
                prompt = f"|wVīta: {caller.db.pv['nunc']}/{caller.db.pv['max']}) |n"

                caller.msg(prompt)
            else:
                pass
        else:
            pass

class Spectā(MuxCommand):
    """
    look at location or object

    Usage:
        spectā
        spectā <rem>

    Beholds your location or objects in your vicinity.
    """

    key = "spectā"
    aliases = ["specta"]
    help_category = 'Iussa Latīna'
    auto_help = True

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller

        # checking out the room
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("Nihil est quod spectāre potes!")
                return

        # Maybe too many arguments?
#        elif  len(self.arglist) != 1:
#            caller.msg("Quid spectāre velis?")
#            return

        # looking at a thing
        else:
            stuff = caller.location.contents + caller.contents
            target, self.args = which_one(self.args, caller, stuff)
            if not target:
                caller.msg(f"'{self.args}' nōn invēnistī!")
                return

            # check grammar of Latin objects
            if hasattr(target, 'db'):
                if target.db.destination:
                    pass
                elif target.db.latin:
                    if check_case(caller, target, self.args, 'acc_sg') == False:
                        return

        self.msg((caller.at_look(target), {"type": "look"}), options=None)

class Cape(MuxCommand):
    """
    Take something.

    Usage:
        cape <rem>

    Lets you move an object from the location you occupy into your
    inventory.
    """

    key = "cape"
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ implements the command """

        caller = self.caller
        latin_caller = False
        latin_target = False
        
        # Check if caller is Latin-language object 
        if hasattr(caller, 'db'):
            if caller.db.Latin:
                latin_caller = True

        # Return an error if there are too many or too few arguments
        if len(self.arglist) != 1:
            caller.msg("Quid capere velis?")
            return

        # Make a list of objects in the caller's location:
        stuff = caller.location.contents

        # Check to see if more than one object has the target's name;
        # Return the target and the args
        target, self.args = which_one(self.args, caller, stuff)
        if not target:
            caller.msg(f"'{self.args}' nōn invēnistī!")
            return

        # Check if target is Latin-language object
        if hasattr(target, 'db'):
            if target.db.Latin:
                latin_target = True

        # Don't let caller take themselves
        if caller == target:
            caller.msg("Tū tē capere nōn potes!")
            return

        # Don't let the caller get non-gettable objects.
        if not target.access(caller, "get"):
            if target.db.et_err_msg:
                caller.msg(target.db.get_err_msg)
                return
            else:
                if latin_target:
                    caller.msg(f"Tū {target.db.formae['acc_sg'][0]} capere nōn potes.")
                    return
                else:
                    caller.msg(f"Tū {target.key} capere nōn potes.")
                    return

        # calling at_before_get hook method
        if not target.at_before_get(caller):
            return

        # If the object and the caller are Latin objects, follow through with
        # evaluating caller's ability to carry anything else
        if latin_caller and latin_target:
            current_carry = caller.db.toll_fer['ferēns']
            carry_max = caller.db.toll_fer['max']
            target_mass = target.db.physical['massa']

            # Make sure proper syntax was used
            if check_case(caller, target, self.args, 'acc_sg') == False:
                return

            # Check to see if character can carry any more weight;
            # Add target mass to burden if caller can carry more
            if current_carry + target_mass > carry_max:
                caller.msg("Tantum ponderis ferre nōn potes!")
                return

            # Check to see if hands are free;
            # If so, put into dominant hand, if free
            if len(caller.db.manibus_plēnīs) >= 2:
                caller.msg("Manūs tuae sunt plēnae!")
                return

            put_into_hand(caller, target)
            caller.db.toll_fer['ferēns'] += target_mass

            caller.msg(f"{target.db.formae['acc_sg'][0]} cēpistī.")
            caller.location.msg_contents(
                    f"{caller.key} {target.db.formae['acc_sg'][0]} cēpit.",
                    exclude=caller
                    )
        else:
            caller.msg(f"{target.key} cēpistī.")
            caller.location.msg_contents(
                    f"{caller.key} {target.key} cēpit.",
                    exclude=caller
                    )

        # move target to inventory if possible
        target.move_to(caller, quiet=True)
        target.at_get(caller)

class Relinque(MuxCommand):
    """
    Get rid of something
    
    Usage:
        relinque <rem>

    Lets you move an object from your inventory into the location
    that you currently occupy.
    """

    key = "relinque"
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ Implement command """

        caller = self.caller
        latin_caller = False
        latin_target = False
        target_direct_object_name = ''
        current_carry = 0

        if hasattr(caller, 'db'):
            if caller.db.latin:
                latin_caller = True
                current_carry = caller.db.toll_fer['ferēns']
        
        if not self.arglist or len(self.arglist) != 1:
            caller.msg("Quid relinquere velis?")
            return

        # Ensure the intended object is targeted
        stuff = caller.contents
        target, self.args = which_one(self.args, caller, stuff)
        if not target:
            caller.msg(f"'{self.args}' nōn invēnistī!")
            return

        # Call the object's scripts at_before_drop() method
        if not target.at_before_drop(caller):
            return

        # Check that the object is a Latin object
        if hasattr(target, 'db'):
            if target.db.latin:
                latin_target = True
                target_direct_object_name = target.db.formae['acc_sg'][0]
                # Check the grammar
                if check_case(caller, target, self.args, 'acc_sg') == False:
                    return
            else:
                target_direct_object_name = target.key


                # Adding the following to deal with clothing:
        if latin_target and latin_caller:
            if target.db.tenētur:
                # New helper function to manage occupied hands
                take_out_of_hand(caller,target)
    #        if target.db.geritur:
    #            target.remove(caller,quiet=True)

            # Lighten the callers toll_fer['ferēns']
            target_mass = target.db.physical['massa']
            caller.db.toll_fer['ferēns'] -= target_mass

        # Move object to caller's location
        target.move_to(caller.location, quiet=True)
        caller.msg(f"{target_direct_object_name} relīquistī.")
        caller.location.msg_contents(f"{caller.name} {target_direct_object_name} relīquit.", exclude=caller)

        # call the object script's at_drop() method.
        target.at_drop(caller)

class Da(MuxCommand):
    """
    give something to someone

    Usage:
        da <rem> <alicuī>
        da <alicuī> <rem>

    gives an item from your inventory to another character,
    placing it in their inventory
    """

    key = "da"
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ implement give """

        # Establish latin status of participants
        caller = self.caller
        latin_caller = False
        latin_target = False
        latin_recipient = False

        caller_carry = 0
        target_mass = 0
        recipient_carry = 0

        # Check whether caller is Latin object
        if hasattr(caller, 'db'):
            if caller.db.latin:
                latin_caller = True
                caller_carry = caller.db.toll_fer['ferēns']

        # Ensure proper number of items in command
        if len(self.arglist) != 2:
            caller.msg("Scrībe: 'da <rem> <alicuī>' vel 'da <alicuī> <rem>'.")
            return

        # Ensure caller has possessions and that there are other characters present
        possessions = caller.contents
        if len(possessions) == 0:
            caller.msg("Nihil habēs.")
            return

        things_in_room = caller.location.contents
        potential_recipients = [r for r in things_in_room if r.typename == 'Persōna']
        if len(potential_recipients) == 0:
            caller.msg("Nēmō adest!")
            return

        everything = possessions + things_in_room

        entity_1, arg1 = which_one(self.arglist[0], caller, everything)
        if not entity_1:
            caller.msg(f"'{arg1}' nōn invēnistī!")
            return
        entity_2, arg2 = which_one(self.arglist[1], caller, everything)
        if not entity_2:
            caller.msg(f"'{arg2}' nōn invēnistī!")
            return

        # Ensure that one of the entities is in possessions and one is in room

        if entity_1 not in possessions and entity_2 not in possessions:
            caller.msg("Quid dare voluistī?")
            return

        if entity_1 not in potential_recipients and entity_2 not in potential_recipients:
            caller.msg("Cui dare voluistī?")
            return

        if entity_1 in possessions:
            target = entity_1
            target_arg = arg1
            recipient = entity_2
            recipient_arg = arg2
        else:
            target = entity_2
            target_arg = arg2
            recipient = entity_1
            recipient_arg = arg1

        # Check whether target is Latin Object
        if hasattr(target, 'db'):
            if target.db.latin:
                latin_target = True
        
                # Ensure caller referred to target in the accusative case:
                if check_case(caller, target, target_arg, 'acc_sg') == False:
                    return

                # Establish target object's status
                target_mass = target.db.physical['massa']
                target_acc_sg = target.db.formae['acc_sg'][0]

        # Ensure caller is either holding the target or has a free hand
        if latin_caller and latin_target:
            if not target.db.tenētur:
                if len(caller.db.manibus_plēnīs) >= 2:
                    caller.msg("Manūs tuae sunt plēnae!")
                    return

        # Ensure caller and recipient are not the same entity:
        if recipient.key == caller.key:
            caller.msg("Tū tibi aliquid dare nōn potes!")
            return

        # Check whether recipient is a Latin Object
        if hasattr(recipient, 'db'):
            if recipient.db.latin:
                latin_recipient = True
                recipient_carry = recipient.db.toll_fer['ferēns']

                # Ensure caller referred to recipient in the dative case
                if check_case(caller, recipient, recipient_arg, 'dat_sg') == False:
                    return

                # Establish recipient's status and encumberance
                recipient_carry = recipient.db.toll_fer['ferēns']
                recipient_max = recipient.db.toll_fer['max']
                recipient_dat_sg = recipient.db.formae['dat_sg'][0]

                # If recipient's too weak, or if hands are full:
                if len(recipient.db.manibus_plēnīs) >= 2:
                    caller.msg(f"Manūs {recipient.db.formae['gen_sg'][0]} sunt plēnae!")
                    recipient.msg(f"{caller.key} tibi {target_acc_sg} dare conāt{us_a_um('nom_sg',caller.db.sexus)}, sed manūs tuae plēnae sunt.")
                    return

                if recipient_carry + target_mass > recipient_max:
                    caller.msg(f"{recipient.key} tantum ponderis ferre nōn potest!")
                    recipient.msg(f"{caller.key} tibi {target_acc_sg} dare conāt{us_a_um('nom_sg',caller.db.sexus)}, sed tū tantum ponderis ferre nōn potes!")
                    return

        # calling at_before_give hook method
        if not target.at_before_give(caller, recipient):
            return

        # Commence the giving!

        # if target is worn, take it off
#        if target.db.geritur:
#            target.remove(caller)
#            caller.msg(f"{target_acc_sg} exuistī.")
#            caller.location.msg_contents(f"{caller.key} {target_acc_sg} exuit.", exclude=caller)
        # Adjust encumberance and occupied hands for latin participants
        if latin_target and latin_caller:
            take_out_of_hand(caller, target)
            caller.db.toll_fer['ferēns'] -= target_mass
        if latin_target and latin_recipient:
            put_into_hand(recipient, target)
            recipient.db.toll_fer['ferēns'] += target_mass

        target.move_to(recipient, quiet=True)
        recipient.msg(f"{caller.key} tibi {target_acc_sg} dedit.")
        caller.msg(f"{target_acc_sg} {recipient_dat_sg} dedistī.")
        caller.location.msg_contents(
                f"{caller.key} {target_acc_sg} {recipient_dat_sg} dedit.",
                exclude=(caller,recipient)
                )
        
        target.at_give(caller, recipient)

class Dīc(MuxCommand):
    """
    Speak as your character

    Usage:
        dīc <message>

    Talk to those in your current location
    """

    key = "dīc"
    aliases = ['dic']
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ run the say command """

        caller = self.caller

        if not self.args:
            caller.msg("Quid dīcere velis?")
            return

        speech = self.args

        # Calling the at_before_say hook on the character
        speech = caller.at_before_say(speech)

        # If speech is empty, stop here
        if not speech:
            return

        # Call the at_after_say hook on the character
        caller.at_say(speech, msg_self=True)

class Mūniātur(ObjManipCommand):
    """
    Build a Latin Room

    Usage:
        mūniātur <room name>, <room genitive>, <room gender> = <exit to here>, <exit to there>

    """

    key = "mūniātur"
    aliases = ['muniatur']
    locks = "cmd:perm(dig) or perm(Builder)"
    help_category = "Iussa Administrātōrum"
    auto_help = True

    # Lockstring of newly created rooms, for easy overloading.
    # Will be formatted with the (id) of the creating object.
    new_room_lockstring = (
            "control:id({id}) or perm(Admin); "
            "delete:id({id}) or perm(Admin); "
            "edit:id({id}) or perm(Admin)"
            )

    def func(self):
        """ Do the building """

        caller = self.caller

        if not self.lhslist or len(self.lhslist) != 3:
            caller.msg("Scrībe: mūniātur <room>, <gen>, <sexus> [= <hūc>, <illūc>]")
            return

        location = caller.location
        nominative = self.lhslist[0]
        genitive = self.lhslist[1]
        sexus = self.lhslist[2]

        # Make sure a proper gender is accepted
        sexus = self.arglist[2]
        if sexus not in ['māre','muliebre','neutrum']:
            caller.msg("Estne sexus 'māre' an 'muliebre' an 'neutrum'?")
            return

        # Make sure an acceptable genitive is submitted
        if not genitive.endswith('ae') and not genitive.endswith('ī') and not genitive.endswith('is') and not genitive.endswith('ūs') and not genitive.endswith('um'):
            caller.msg("Eheu, ista forma cāsūs genitīvī nōn est accipienda.")
            return

        # Testing
        caller.msg(f"Our location: {location.key}")

        # Create the new room
        typeclass = Locus
        new_room = create.create_object(
                typeclass,
                nominative,
                attributes=[
                    ("formae",{"nom_sg":[nominative],"gen_sg":[genitive]}),
                    ("sexus",sexus),
                    ],
                    report_to=caller,
                )
        lockstring = self.new_room_lockstring.format(id=caller.id)
        new_room.locks.add(lockstring)
        alias_string = ""
        if new_room.aliases.all():
            alias_string = " (%s)" % ", ".join(new_room.aliases.all())
        room_string = f"Created room {new_room.key}({new_room.dbref}), {genitive} of type {new_room.typename}"
        caller.msg(room_string)

        # Check to see if exits should be created
        if self.rhslist:
            if self.rhslist[0] == '-':
                exit_to_here = False
            else:
                exit_to_here = self.rhslist[0]
            if self.rhslist[1]:
                if self.rhslist[1] == '-':
                    exit_to_there = False
                else:
                    exit_to_there = self.rhslist[1]

        else:
            if location.db.lang == 'latin':
                exit_to_here = f"ad {location.db.formae['acc_sg'][0]}"
            else:
                exit_to_here = f"ad {location.key}"
            exit_to_there = f"ad {new_room.db.formae['acc_sg'][0]}"

        # Create exit to here
        if exit_to_here:
            typeclass = Exitus
            new_exit_to_here = create.create_object(
                    typeclass=typeclass,
                    key=exit_to_here,
                    location=new_room,
                    locks = lockstring,
                    destination = location,
                    report_to = caller,
                    )
            alias_string = ""
            if new_exit_to_here.aliases.all():
                alias_string = " (%s)" % ", ".join(new_exit_to_here.aliases.all())
            exit_to_here_string = f"\nCreated exit from {new_room.name} to {location.name}: {exit_to_here}({new_exit_to_here.dbref}) {alias_string}"
            caller.msg(exit_to_here_string)

        # Create exit to there
        if exit_to_there:
            typeclass = Exitus
            new_exit_to_there = create.create_object(
                    typeclass=typeclass,
                    key=exit_to_there,
                    location=location,
                    locks = lockstring,
                    destination = new_room,
                    report_to = caller
                    )
            alias_string = ""
            if new_exit_to_there.aliases.all():
                alias_string = " (%s)" % ", ".join(new_exit_to_there.aliases.all())
            exit_to_there_string = f"\nCreated exit from {location.name} to {new_room.name}: {exit_to_there}({new_exit_to_there.dbref}) {alias_string}"
            caller.msg(exit_to_there_string)

class Creātur(MuxCommand):
    """
    Create an object with grammatical gender, a nominative singular,
    and a genitive singular form.

    Usage:
        creātur <nom_sg> <gen_sg> <gender> <typeclass>

    """

    key = "creātur"
    aliases = ['creatur']
    locks = "cmd:perm(Builders)"
    help_category = "Iussa Administrātōrum"
    auto_help = True

    def parse(self):

        arglist = [arg.strip() for arg in self.args.split()]

        self.arglist = arglist

    def func(self):
        """
        Creates the object.
        """

        caller = self.caller

        # Make sure the proper number of arguments are used
        if not self.args or len(self.arglist) != 4:
            caller.msg("Scrībe: creātur <nōminātīvus cāsus> <genetīvus cāsus> <sexus> <genus>")
            return

        # Make sure a proper gender is accepted
        sexus = self.arglist[2]
        if sexus not in ['māre','muliebre','neutrum']:
            caller.msg("Estne sexus 'māre' an 'muliebre' an 'neutrum'?")
            return

        # Make sure an acceptable genitive is submitted
        genitive = self.arglist[1]
        if not genitive.endswith('ae') and not genitive.endswith('ī') and not genitive.endswith('is') and not genitive.endswith('ūs') and not genitive.endswith('um'):
            caller.msg("Eheu, ista forma cāsūs genitīvī nōn est accipienda.")
            return

        # create the object
        name = self.arglist[0]
#        typeclass = 'rēs'
        typeclass = f"typeclasses.rēs.{self.arglist[3]}"
        
        # create object (if not a valid typeclass, the default
        # object typeclass will automatically be used)
#        lockstring = self.new_obj_lockstring.format(id=caller.id)
        obj = create.create_object(
                typeclass,
                name,
                caller,
                home=caller,
#                locks=lockstring,
                report_to=caller,
                attributes=[
                    ('lang', 'latin'),
                    ('sexus', sexus),
                    ('formae',{'nom_sg': [name], 'gen_sg': [genitive]}),
                    ]
                )
        message = f"Ā tē nova {obj.typename} creāta est: {obj.name}."
        if not obj:
            return
        if not obj.db.desc:
            obj.db.desc = "Nihil ēgregiī vidēs."

        caller.msg(message)

class Nascātur(MuxCommand):
    """
    Create an NPC

    Usage:
        nascātur <praenomen>, [<nomen>], <sexus> = <genitive praenomen>, <genitive nomen>

    """

    key = "nascātur"
    aliases = ["nascatur"]
    locks = "cmd:perm(Builder)"
    help_category = "Iussa Administrātōrum"
    auto_help = True

    def func(self):
        """
        The command for creating an NPC itself
        """

        caller = self.caller

        self.nōmen = None
        self.nōmen_gen = None
        self.gens = None

        sexus = {'māre': 'masculine', 'muliebre': 'feminine'}

        if not self.args:
            self.sexus = choice(list(sexus.keys()))
            self.gender = sexus[self.sexus]
            self.gens = choice(list(name_data.keys()))
            self.praenōmen = choice(name_data[self.gens]['praenomina'][self.gender])
            if self.sexus == 'muliebre':
                self.nōmen = self.gens
            elif self.sexus == 'māre':
                self.nōmen = self.gens[:-1] + 'us'
            else:
                self.nōmen = self.gens[:-1] + 'um'

            if self.sexus == 'muliebre':
                self.praenōmen_gen = self.praenōmen + 'e'
                self.nōmen_gen = self.nōmen + 'e'
            else:
                self.nōmen_gen = self.nōmen[:-2] + 'ī'
                if self.praenōmen == 'Opiter':
                    self.praenōmen_gen = 'Opitris'
                elif self.praenōmen == 'Caesō':
                    self.praenōmen_gen = 'Caesōnis'
                elif self.praenōmen == 'Sertor':
                    self.praenōmen_gen = 'Sertōris'
                else:
                    self.praenōmen_gen = self.praenōmen[:-2] + 'ī'
            nōmina = self.praenōmen + ' ' + self.nōmen

        elif not self.rhslist:
            caller.msg("Usage: nascātur [<praenōmen>, [<nōmen>], <sexus> = <praenōminis>, [<nōminis>]]")
        elif self.lhslist[-1] not in ['māre', 'muliebre', 'neutrum']:
            caller.msg("Usage: nascātur [<praenōmen>, [<nōmen>], <sexus> = <praenōminis>, [<nōminis>]]")
        elif len(self.lhslist) > 2 and len(self.rhslist) == 2:
            self.praenōmen = self.lhslist[0]
            self.praenōmen_gen = self.rhslist[0]
            self.nōmen = self.lhslist[1]
            self.nōmen_gen = self.rhslist[1]
            self.sexus = self.lhslist[2]
            if self.sexus == 'muliebre':
                self.gens = self.nōmen
            else:
                self.gens = self.nōmen[:-2] + 'a'
        else:
            self.praenōmen = self.lhslist[0]
            self.praenōmen_gen = self.rhslist[0]
            self.sexus = self.lhslist[1]

        if self.nōmen:
            nōmina = self.praenōmen + ' ' + self.nōmen
        else:
            nōmina = self.praenōmen
#        home = 56
        home = ObjectDB.objects.get_id(settings.DEFAULT_HOME)
        typeclass = 'typeclasses.persōnae.Persōna'

        nom_sg = [self.praenōmen]
        gen_sg = [self.praenōmen_gen]

        if self.nōmen:
            nom_sg.append(self.nōmen)
            gen_sg.append(self.nōmen_gen)

        char = create.create_object(
                typeclass = typeclass,
                key = nōmina,
                home = home,
                location = caller.location,
                attributes = [
                    ('lang', 'latin'),
                    ('sexus', self.sexus),
                    ('gens', self.gens),
                    ('praenōmen', self.praenōmen),
                    ('nōmen', self.nōmen),
                    ('formae',{
                        'nom_sg': nom_sg,
                        'gen_sg': gen_sg,
#                        'nom_sg': [self.praenōmen,self.nōmen],
#                        'gen_sg': [self.praenōmen_gen,self.nōmen_gen],
                        }
                        )
                    ]
                )

        caller.location.msg_contents(f"{nōmina} nāt{us_a_um('nom_sg',self.sexus)} est!")



class Pōne(MuxCommand):
    """
    Place one object inside of another in your possession or in your location

    Usage:
        pōne <rem> in <rem>

    Store things in containers
    """

    key = "pōne"
    aliases = ['pone']
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ run the put command """

        caller = self.caller

        # Ensure proper syntax
        if len(self.arglist) != 3:
            caller.msg("Usage: pōne <rem> in <rem>")
            return
        elif 'in' not in self.arglist:
            caller.msg("Usage: pōne <rem> in <rem>")
            return
        elif self.arglist[-1] == 'in':
            caller.msg("Usage: pōne <rem> in <rem>")
            return

        # Identify target and container
        if self.arglist[0] == 'in':
            intended_target = self.arglist[2]
            intended_container = self.arglist[1]
        else:
            intended_target = self.arglist[0]
            intended_container = self.arglist[2]

        # identify target
        possessions = caller.contents
        target, intended_target = which_one(intended_target,caller,possessions)
        if not target:
            caller.msg(f"'{intended_target}' nōn invēnistī!")
            return

        # check grammar of Latin objects
        if hasattr(target, 'db'):
            if target.db.latin:
                if check_case(caller, target, intended_target, 'acc_sg') == False:
                    return

        # ensure object is in hands
        if not target.db.tenētur:
            caller.msg(f"{target.db.formae['acc_sg'][0]} nōn tenēs!")
            return

        # identify container
        stuff = caller.contents + caller.location.contents
        container, intended_container = which_one(intended_container,caller,stuff)
        if not container:
            caller.msg(f"'{intended_container}' nōn invēnistī!")
            return

        # check grammar of Latin objects
        if hasattr(container, 'db'):
            if container.db.latin:
                if check_case(caller, container, intended_container, 'acc_sg') == False:
                    return

        # ensure container *is* a container:
        if not container.db.capax:
            caller.msg(f"{container.key} nihil tenēre potest!")
            return

        # don't let something be put into itself!
        if target == container:
            caller.msg(f"{target.name} in sē pōnī nōn potest!")
            return

        # Manage volume and dimensions of target and container
        target_volume = target.db.physical['litra']
        container_max_volume = container.db.capax['max_vol']
        container_remaining_volume = container.db.capax['rem_vol']

        if target_volume > container_remaining_volume:
            caller.msg(f"Magnitūdō {target.db.formae['gen_sg'][0]} est māior quam spatium in {container.db.formae['abl_sg'][0]}.")
            return

        if target.db.physical['rigēns'] == True:
            target_dimensions = [
                    target.db.physical['x'],
                    target.db.physical['y'],
                    target.db.physical['z'],
                    ]
            container_dimensions = [
                    container.db.capax['x'],
                    container.db.capax['y'],
                    container.db.capax['z'],
                    ]
            target_dimensions.sort()
            container_dimensions.sort()
            # Allow for objects sticking at most half out of container
            if target_dimensions[2] / 2 > container.db.capax['y'] and target_dimensions[2] > container_dimensions[2]:
                caller.msg(f"{container.name} satis alt{us_a_um('nom_sg',container.db.sexus)} nōn est!")
                return
            elif target_dimensions[1] > container_dimensions[1] or target_dimensions[0] > container_dimensions[0]:
                caller.msg(f"Forma {target.db.formae['gen_sg'][0]} ad {container.db.formae['acc_sg'][0]} apt{us_a_um('nom_sg',target.db.sexus)} nōn est!")
                return

        # Make the move happen
        caller.msg(f"{target.db.formae['acc_sg'][0]} in {container.db.formae['acc_sg'][0]} posuistī.")
        caller.location.msg_contents(f"{caller.name} {target.db.formae['acc_sg'][0]} in {container.db.formae['acc_sg'][0]} posuit.",exclude=caller)
        container.db.capax['rem_vol'] -= target.db.physical['litra']
        take_out_of_hand(caller,target)
        target.move_to(container, quiet=True)

        # If container isn't rigid, increase its volume
        if not container.db.physical['rigēns']:
            container.db.physical['litra'] += target.db.physical['litra']

        # If caller isn't holding the container, fix the encumberance
        if container not in possessions:
            caller.db.toll_fer['ferēns'] -= target.db.physical['massa']

        # adjust the mass of the container
        container.db.physical['massa'] += target.db.physical['massa']

        return

class Excipe(MuxCommand):
    """
    Take something out of something else

    Usage:
        excipe <rem> ē/ex <rē>

    """

    key = "excipe"
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ run the put command """

        caller = self.caller

        # Ensure proper syntax
        if len(self.arglist) != 3:
            caller.msg("Usage: excipe <rem> ē/ex <rē>")
            return
        elif 'ē' not in self.arglist and 'e' not in self.arglist and 'ex' not in self.arglist:
            caller.msg("Usage: excipe <rem> ē/ex <rē>")
            return
        elif self.arglist[-1] == 'e' or self.arglist[-1] == 'ē' or self.arglist[-1] == 'ex':
            caller.msg("Usage: excipe <rem> ē/ex <rē>")
            return

        # Identify target and container
        if self.arglist[0] == 'ex' or self.arglist[0] == 'e' or self.arglist[0] == 'ē':
            intended_target = self.arglist[2]
            intended_container = self.arglist[1]
        else:
            intended_target = self.arglist[0]
            intended_container = self.arglist[2]

        # identify container
        stuff = caller.contents + caller.location.contents
        container, intended_container = which_one(intended_container,caller,stuff)
        if not container:
            caller.msg(f"'{intended_container}' nōn invēnistī!")
            return

        # check grammar of Latin objects
        if hasattr(container, 'db'):
            if container.db.latin:
                if check_case(caller, container, intended_container, 'abl_sg') == False:
                    return
        
        # Ensure intended container can contain things
        if not container.db.capax:
            caller.msg(f"{container.name} nihil continēre potest")
            return

        # identify target
        contents = container.contents
        target, intended_target = which_one(intended_target,caller,contents)
        if not target:
            caller.msg(f"'{intended_target}' nōn invēnistī!")
            return

        # check grammar of Latin objects
        if hasattr(target, 'db'):
            if target.db.latin:
                if check_case(caller, target, intended_target, 'acc_sg') == False:
                    return

        # Don't let the caller get non-gettable objects.
        if not target.access(caller, "get"):
            if target.db.et_err_msg:
                caller.msg(target.db.get_err_msg)
                return
            else:
                if target.db.latin:
                    caller.msg(f"Tū {target.db.formae['acc_sg'][0]} capere nōn potes.")
                    return
                else:
                    caller.msg(f"Tū {target.key} capere nōn potes.")
                    return

        # calling at_before_get hook method
        if not target.at_before_get(caller):
            return
        latin_caller = False
        latin_target = False

        if caller.db.latin:
            latin_caller = True
        if target.db.latin:
            latin_target = True

        # If the object and the caller are Latin objects, follow through with
        # evaluating caller's ability to carry anything else
        if latin_caller and latin_target:
            current_carry = caller.db.toll_fer['ferēns']
            carry_max = caller.db.toll_fer['max']
            target_mass = target.db.physical['massa']

            # Check to see if character can carry any more weight;
            # Add target mass to burden if caller can carry more
            if current_carry + target_mass > carry_max:
                caller.msg("Tantum ponderis ferre nōn potes!")
                return

            # Check to see if hands are free;
            # If so, put into dominant hand, if free
            if len(caller.db.manibus_plēnīs) >= 2:
                caller.msg("Manūs tuae sunt plēnae!")
                return

            put_into_hand(caller, target)
            if container.location != caller:
                caller.db.toll_fer['ferēns'] += target_mass

            caller.msg(f"{target.db.formae['acc_sg'][0]} ex {container.db.formae['abl_sg'][0]} cēpistī.")
            caller.location.msg_contents(
                    f"{caller.key} {target.db.formae['acc_sg'][0]} ex {container.db.formae['abl_sg'][0]} cēpit.",
                    exclude=caller
                    )
        else:
            caller.msg(f"{target.key} ex {container.key} cēpistī.")
            caller.location.msg_contents(
                    f"{caller.key} {target.key} ex {container.key} cēpit.",
                    exclude=caller
                    )

        # move target to inventory if possible
        target.move_to(caller, quiet=True)
        target.at_get(caller)

        # If non-rigid container, reduce its volume
        if container.db.physical['rigēns']:
            container.db.physical['litra'] -= target.db.physical['litra']

        # Remove the mass of the target from the mass of the container
        container.db.physical['massa'] -= target.db.physical['massa']

class Inspice(MuxCommand):
    """
    Look inside of a container

    Usage:
        inspice in <rem>
    """

    key = "inspice"
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ handle the looking. """

        caller = self.caller

        if not self.args:
            caller.msg("Usage: inscpice in <rem>")
            return
        elif len(self.arglist) != 2:
            caller.msg("Usage: inscpice in <rem>")
            return
        elif self.arglist[0] != 'in':
            caller.msg("Usage: inscpice in <rem>")
            return

        intended_container = self.arglist[1]

        # identify container
        stuff = caller.contents + caller.location.contents
        container, intended_container = which_one(intended_container,caller,stuff)
        if not container:
            caller.msg(f"'{intended_container}' nōn invēnistī!")
            return

        # check grammar of Latin objects
        if hasattr(container, 'db'):
            if container.db.latin:
                if check_case(caller, container, intended_container, 'acc_sg') == False:
                    return
        
        # Ensure intended container can contain things
        if not container.db.capax:
            caller.msg(f"{container.name} nihil continēre potest!")
            return

        items = container.contents
        if not items:
            string = f"Nihil in {container.db.formae['abl_sg'][0]} est."
        else:
            table = self.styled_table(border="header")
            for item in items:
                table.add_row("|C%s|n" % item.name, item.db.desc or "")
            string = "|wEcce:\n%s" % table
        self.caller.msg(string)

class Tenē(MuxCommand):
    """
    Hold something in a particular hand

    Usage:
        tenē <rem> <dextrā>/<sinistrā>

    """

    key = "tenē"
    aliases = ["tene"]
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ implements the command """

        caller = self.caller

        # Make sure computer syntax is satisfied
        if not self.args:
            caller.msg("Quid tenēre velis?")
            return
        elif len(self.arglist) != 2:
            caller.msg("Usage: tenē <rem> <dextrā>/<sinistrā>")
            return

        hand_specified = False
        hands = ['dextrā','dextra','sinistrā','sinistra']
        for arg in self.arglist:
            if arg in hands:
                hand_specified = arg
                break

        if not hand_specified:
            caller.msg("Quā manū tenēre velis?")
            return

        # Get the macrons onto the hand:
        if hand_specified == 'dextra':
            hand_specified = 'dextrā'
        elif hand_specified == 'sinistra':
            hand_specified = 'sinistrā'

        # Identify target
#        self.arglist.remove(hand_specified)
        intended_target = None
        for sa in self.arglist:
            if unidecode(sa) != unidecode(hand_specified):
                intended_target = sa
#        no_hands = arguments.remove(hand_specified)
#        intended_target = no_hands[0]

        stuff = caller.location.contents
        for con in caller.contents:
            if con.db.tenētur:
                stuff.append(con)

        target, intended_target = which_one(intended_target,caller,stuff)
        if not target:
            caller.msg(f"'{intended_container}' nōn invēnistī!")
            return

        if target.db.latin:
            if check_case(caller, target, intended_target, 'acc_sg') == False:
                return

        # If intended hand is full, report to caller
        if target.db.tenētur == hand_specified:
            caller.msg(f"{target.db.formae['acc_sg'][0]} illā manū iam tenēs!")
            return
        elif hand_specified in caller.db.manibus_plēnīs:
            caller.msg(f"Illa manus aliquid iam tenet!")
            return

        # Don't let the caller get non-gettable objects.
        if not target.access(caller, "get"):
            if target.db.et_err_msg:
                caller.msg(target.db.get_err_msg)
                return
            else:
                if latin_target:
                    caller.msg(f"Tū {target.db.formae['acc_sg'][0]} capere nōn potes.")
                    return
                else:
                    caller.msg(f"Tū {target.key} capere nōn potes.")
                    return

        # calling at_before_get hook method
        if not target.at_before_get(caller):
            return

        # Put into hand
        if target.db.tenētur:
            caller.db.manibus_vacuīs.append(target.db.tenētur)
            caller.db.manibus_vacuīs.remove(hand_specified)
            caller.db.manibus_plēnīs.remove(target.db.tenētur)
            caller.db.manibus_plēnīs.append(hand_specified)
            target.db.tenētur = hand_specified
        else:
            if target.db.physical['massa'] + caller.db.toll_fer['ferēns'] > caller.db.toll_fer['max']:
                caller.msg("Tantum ponderis ferre nōn potes!")
                return
            else:
                target.db.tenētur = hand_specified
                target.move_to(caller,quiet=True)
                target.at_get(caller)
                caller.db.manibus_plēnīs.append(hand_specified)
                caller.db.manibus_vacuīs.remove(hand_specified)
                caller.db.toll_fer['ferēns'] += target.db.physical['massa']

        caller.msg(f"{target.db.formae['acc_sg'][0]} {hand_specified} tenēs.")
        caller.location.msg_contents(f"{caller.name} {target.db.formae['acc_sg'][0]} {hand_specified} tenet.",exclude=caller)

class Ligā(MuxCommand):
    """
    Allows instumental ablative use of ligatures to direct objects

    Usage:
        ligā <rem> <rē>

    Bind something with something else
    """

    key = "ligā"
    aliases = ['liga']
    locks = 'cmd:all()'
    help_category = 'Iussa Latiīna'
    auto_help = True

    def func(self):
        """
        Handle the binding, setting a "ligāta" tag on the target with the ligature as value,
        and setting the "ligāns" tag on the instrument with the target as value.
        """

        caller = self.caller

        # Ensure computer syntax is ok
        if not self.args or len(self.arglist) != 2:
            caller.msg("Usage: ligā <rem> <rē>")
            return

        arg1 = self.arglist[0]
        arg2 = self.arglist[1]

        possessions = caller.contents
        everything = caller.location.contents + possessions


        ligature = False
        # Make sure that caller is holding a ligature
        for p in possessions:
            if p.db.tenētur and p.typename == 'Ligātūra':
                ligature = p

        if not ligature:
            caller.msg('Nūllum tenēs quō ligāre potes.')
            return

        # Idnetify ligature and target
        entity1, arg1 = which_one(arg1, caller, everything)
        if not entity1:
            caller.msg(f"'{arg1}' nōn invēnistī!")
            return
        entity2, arg2 = which_one(arg2, caller, everything)
        if not entity2:
            caller.msg(f"'{arg2}' nōn invēnistī!")
            return

        if entity1 in [ligature]:
            target = entity2
            target_arg = arg2
            ligature_arg = arg1
        else:
            target = entity1
            target_arg = arg1
            ligature_arg = arg2

        # Don't let a ligature bind itself
        if target == ligature:
            caller.msg("Ligātūra sē ligārī nōn potest!")
            return

        # Make sure the ligature isn't already tying something else
        if ligature.db.ligāns:
            caller.msg(f"Aliquid {ligature.db.formae['abl_sg'][0]} iam ligātum est!")
            return

        # Check Grammar
        if check_case(caller, target, target_arg, 'acc_sg') == False:
            return

        if check_case(caller, ligature, ligature_arg, 'abl_sg') == False:
            return

        target.db.ligāta = ligature.dbref
        ligature.db.ligāns = target.dbref

        target_acc = target.db.formae['acc_sg'][0]
        ligature_abl = ligature.db.formae['abl_sg'][0]
        caller_nom = caller.db.formae['nom_sg'][0]
        ligature_sexus = ligature.db.sexus

        caller.msg(f"{target_acc} {ligature_abl} ligāvistī.")
        target.msg(f"{caller_nom} tē {ligature_abl} ligāvit.")
        caller.location.msg_contents(
                f"{caller_nom} {target_acc} {ligature_abl} ligāvit", 
                exclude=(caller,target)
                )

        target.db.descriptive_name = f"{target.name} {ligature_abl} ligāt{us_a_um('nom_sg',target.db.sexus)} qu{'em' if ligature_sexus == 'māre' else 'am' if ligature_sexus == 'muliebre' else 'od'} tenet {caller_nom}." 

class Solve(MuxCommand):
    """
    Loosen something from a ligature

    Usage:
        solve <rem> <rē>

    """

    key = "solve"
    aliases = ["solue"]
    locks = "cmd:all()"
    help_category = "Iussa Latīna"
    auto_help = True

    def func(self):
        """ implements the command """

        caller = self.caller

        # Make sure computer syntax is satisfied
        if not self.args:
            caller.msg("Quid quō solvere velis?")
            return
        elif len(self.arglist) != 2:
            caller.msg("Usage: solve <rem> <rē>")
            return

        arg1 = self.arglist[0]
        arg2 = self.arglist[1]

        bound_objects = []
        possessions = caller.contents
        everything = caller.location.contents + possessions
        for e in everything:
            if e.db.ligāta:
                bound_objects.append(e)

        if len(bound_objects) == 0:
            caller.msg("Nihil hīc ligātum est!")
            return

        # Idnetify ligature and target
        entity1, arg1 = which_one(arg1, caller, bound_objects)
        entity2, arg2 = which_one(arg2, caller, bound_objects)

        if entity1:
            target = entity1
            target_arg = arg1
            ligature_arg = arg2
        elif entity2:
            target = entity2
            target_arg = arg2
            ligature_arg = arg1
        else:
            caller.msg("Quid quō solvere velis?")
            return

        ligature = Ligātūra.objects.get(id=target.db.ligāta[1:])

        # Check Grammar
        if check_case(caller, target, target_arg, 'acc_sg') == False:
            return

        if check_case(caller, ligature, ligature_arg, 'abl_sg') == False:
            return

        target.db.ligāta = False
        ligature.db.ligāns = False

        target_acc = target.db.formae['acc_sg'][0]
        ligature_abl = ligature.db.formae['abl_sg'][0]
        caller_nom = caller.db.formae['nom_sg'][0]
        ligature_sexus = ligature.db.sexus

        caller.msg(f"{target_acc} {ligature_abl} solvistī.")
        target.msg(f"{caller_nom} tē {ligature_abl} solvit.")
        caller.location.msg_contents(
                f"{caller_nom} {target_acc} {ligature_abl} solvit", 
                exclude=(caller,target)
                )

        target.db.descriptive_name = False

class IussaLatīnaCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for the Latin commands.
    """

    key = "Persōna"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        self.add(Cape())
#        self.add(Relinque())
#        self.add(Da())
        self.add(Dīc())
        self.add(Spectā())
        self.add(Pōne())
        self.add(Excipe())
        self.add(Inspice())
        self.add(Tenē())
        self.add(Ligā())
        self.add(Solve())

class IussaAdministrātōrumCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for building and creating Latin objects.
    """

    key = "Persōna"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        self.add(Creātur())
        self.add(Mūniātur())
        self.add(Nascātur())

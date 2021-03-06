# file mygame/commands/iussa.py
"""
Iussa

Iussa describe the Latin commands and syntax for interacting with the world

"""

from evennia.commands.default import muxcommand
from evennia.utils import create
from evennia import default_cmds

from evennia.commands.default.building import ObjManipCommand

from utils.latin_language.adjective_agreement import us_a_um
from utils.latin_language.which_one import which_one
from utils.latin_language.check_grammar import check_case
from utils.latin_language.free_hands import free_hands, put_into_hand, take_out_of_hand

from typeclasses.locī import Locus
from typeclasses.exitūs import Exitus

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
        elif  len(self.arglist) != 1:
            caller.msg("Quid spectāre velis?")
            return

        # looking at a thing
        else:
            stuff = caller.location.contents + caller.contents
            target, self.args = which_one(self.args, caller, stuff)
            if not target:
                return

            # check grammar of Latin objects
            if hasattr(target, 'db'):
                if target.db.latin:
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
            return
        entity_2, arg2 = which_one(self.arglist[1], caller, everything)
        if not entity_2:
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
                alias_string = " (%s)" % ", ".join(new_exit_to_there.aleases.all())
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

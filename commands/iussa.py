# file mygame/commands/iussa.py
"""
Iussa

Iussa describe the Latin commands and syntax for interacting with the world

"""

from evennia.commands.default import muxcommand
from evennia import default_cmds

from utils.latin_language.adjective_agreement import us_a_um
from utils.latin_language.which_one import which_one
from utils.latin_language.check_grammar import check_case
from utils.latin_language.free_hands import free_hands, put_into_hand, take_out_of_hand

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
            else:
                caller.db.toll_fer['ferēns'] += target_mass

            # Check to see if hands are free;
            # If so, put into dominant hand, if free
            if len(caller.db.manibus_plēnīs) >= 2:
                caller.msg("Manūs tuae sunt plēnae!")
            else:
                put_into_hand(caller, target)

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

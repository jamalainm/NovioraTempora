# file mygame/commands/clothing_commands.py
#
# Heavliy based on Tim Ashley Jenkins 2017 Evennia contribution
#
# Moved from the 'latin_clothing' typeclass file for consistency's sake
#
# COMMANDS START HERE

from commands.iussa import MuxCommand
from evennia import default_cmds
from evennia.utils import evtable
from utils.latin_language.which_one import which_one
from utils.latin_language.check_grammar import check_case
from utils.latin_language.free_hands import take_out_of_hand, put_into_hand
from typeclasses.vestīmenta import CLOTHING_TYPE_LIMIT, CLOTHING_OVERALL_LIMIT, get_worn_clothes, single_type_count

class Indue(MuxCommand):
    """
    Puts on an item of clothing you are holding.

    Usage:
      indue <rem> 

    Examples:
      indue tunicam

    All the clothes you are wearing are appended to your description.
    If you provide a 'wear style' after the command, the message you
    provide will be displayed after the clothing's name.
    """

    # JI (12/17/19) changing key to 'indue' and help category to 
    # 'Iussa Latīna'
    key = "indue"
    help_category = "Iussa Latīna"

    def func(self):
        """
        This performs the actual command.
        """
        caller = self.caller
        if not self.args:
            # JI (12/17/19) adapting for Latin commands, removing "wear style"
            self.caller.msg("Usage: indue <rem>")
            return
        # JI (12/7/19) Commenting out following line, adding my which_one function
        # and copying the commented out line with self.arglist[0] replaced by target
        # clothing = self.caller.search(self.arglist[0], candidates=self.caller.contents)
        stuff = self.caller.contents
        target, self.args = which_one(self.args,self.caller,stuff)
        # JI (12/7/19) Going to see about bypassing the following in preference of the above
        # clothing = self.caller.search(target, candidates=self.caller.contents)
        clothing = target
        wearstyle = True
        if not clothing:
            # JI (12/7/19) changing to Latin
            self.caller.msg("Nōn in manibus habēs.")
            return
        if not clothing.is_typeclass("typeclasses.vestīmenta.Vestīmentum", exact=False):
            # JI (12/7/19) adapting to Latin
            self.caller.msg("Ill%s non est vestīmentum!" % ('a' if clothing.db.sexus == 'muliebre' else 'e' if clothing.db.sexus == 'māre' else 'ud'))
            return

        # Enforce overall clothing limit.
        if CLOTHING_OVERALL_LIMIT and len(get_worn_clothes(self.caller)) >= CLOTHING_OVERALL_LIMIT:
            # JI (12/7/19) Adapting to Latin
            self.caller.msg("Plūra vestīmenta gerere nōn potes!")
            return

        # Apply individual clothing type limits.
        if clothing.db.genus_vestīmentōrum and not clothing.db.geritur:
            type_count = single_type_count(get_worn_clothes(self.caller), clothing.db.genus_vestīmentōrum)
            if clothing.db.genus_vestīmentōrum in list(CLOTHING_TYPE_LIMIT.keys()):
                if type_count >= CLOTHING_TYPE_LIMIT[clothing.db.genus_vestīmentōrum]:
                    self.caller.msg("Vestīmenta huius generis plūra gerere nōn potes!")
                            # JI (12/7/19) Adapting to Latin
#                        "You can't wear any more clothes of the type '%s'."
#                        % clothing.db.genus_vestīmentōrum
#                    )

                    return

        if clothing.db.geritur and len(self.arglist) == 1:
            # JI (12/7/19) Adapting to Latin
            self.caller.msg("Iam %s geris!" % clothing.db.formae['acc_sg'][0])
            return
        if len(self.arglist) > 1:  # If wearstyle arguments given
            wearstyle_list = self.arglist  # Split arguments into a list of words
            del wearstyle_list[0]  # Leave first argument (the clothing item) out of the wearstyle
            wearstring = " ".join(
                str(e) for e in wearstyle_list
            )  # Join list of args back into one string
            if (
                WEARSTYLE_MAXLENGTH and len(wearstring) > WEARSTYLE_MAXLENGTH
            ):  # If length of wearstyle exceeds limit
                self.caller.msg(
                    "Please keep your wear style message to less than %i characters."
                    % WEARSTYLE_MAXLENGTH
                )
            else:
                wearstyle = wearstring
        # JI (12/7/19) Make sure grammar happens:
        if check_case(self.caller, target, self.args, 'acc_sg') == False:
            return
        clothing.wear(self.caller, wearstyle)



class Exue(MuxCommand):
    """
    Takes off an item of clothing.

    Usage:
       exue <rem>

    Removes an item of clothing you are wearing. You can't remove
    clothes that are covered up by something else - you must take
    off the covering item first.
    """

    key = "exue"
    help_category = "Iussa Latīna"

    def func(self):
        """
        This performs the actual command.
        """
        # JI (12/7/19) Like with CmdWear above, adding the which_one function
        # to deal with Latin issues. Commenting out original and adapting by
        # changing self.args to target.
        # clothing = self.caller.search(self.args, candidates=self.caller.contents)
        stuff = self.caller.contents
        target, self.args = which_one(self.args,self.caller,stuff)
        # JI (12/7/9) commenting out the below in preference of the above
        # clothing = self.caller.search(target, candidates=self.caller.contents)
        clothing = target
        if not clothing:
            # JI (12/7/19) Adapted to Latin
            self.caller.msg("Non geritur.")
            return
        if not clothing.db.geritur:
            # JI (12/7/19) Adapted to Latin
            self.caller.msg("Non geritur!")
            return
        if clothing.db.covered_by:
            # adapted to Latin
            self.caller.msg("prius tibi est necesse %s exuere." % clothing.db.covered_by.db.formae['acc_sg'][0])
            return
        # JI (12/7/19) Ensure proper grammer
        lower_case = [x.lower() for x in clothing.db.formae['acc_sg']]
        if self.args.lower() not in lower_case:
            self.caller.msg(f"(Did you mean '{clothing.db.formae['acc_sg']}'?)")
            return
        clothing.remove(self.caller)


class CmdCover(MuxCommand):
    # JI 12/7/19
    # I think the syntax for adapting this command could take a while:
    # since there are multiple arguments we want to accept either word
    # order and if I remember from the 'give' command adaptation, that
    # was a failry involved process
    """
    Covers a worn item of clothing with another you're holding or wearing.

    Usage:
        cover <obj> [with] <obj>

    When you cover a clothing item, it is hidden and no longer appears in
    your description until it's uncovered or the item covering it is removed.
    You can't remove an item of clothing if it's covered.
    """

    key = "cover"
    help_category = "clothing"

    def func(self):
        """
        This performs the actual command.
        """

        if len(self.arglist) < 2:
            self.caller.msg("Usage: cover <worn clothing> [with] <clothing object>")
            return
        # Get rid of optional 'with' syntax
        if self.arglist[1].lower() == "with" and len(self.arglist) > 2:
            del self.arglist[1]
        to_cover = self.caller.search(self.arglist[0], candidates=self.caller.contents)
        cover_with = self.caller.search(self.arglist[1], candidates=self.caller.contents)
        if not to_cover or not cover_with:
            return
        if not to_cover.is_typeclass("typeclasses.vestīmenta.Vestīmentum", exact=False):
            self.caller.msg("%s isn't clothes!" % to_cover.name)
            return
        if not cover_with.is_typeclass("typeclasses.vestīmenta.Vestīmentum", exact=False):
            self.caller.msg("%s isn't clothes!" % cover_with.name)
            return
        if cover_with.db.genus_vestīmentōrum:
            if cover_with.db.genus_vestīmentōrum in CLOTHING_TYPE_CANT_COVER_WITH:
                self.caller.msg("You can't cover anything with that!")
                return
        if not to_cover.db.geritur:
            self.caller.msg("You're not wearing %s!" % to_cover.name)
            return
        if to_cover == cover_with:
            self.caller.msg("You can't cover an item with itself!")
            return
        if cover_with.db.covered_by:
            self.caller.msg("%s is covered by something else!" % cover_with.name)
            return
        if to_cover.db.covered_by:
            self.caller.msg(
                "%s is already covered by %s." % (cover_with.name, to_cover.db.covered_by.name)
            )
            return
        if not cover_with.db.geritur:
            cover_with.wear(
                self.caller, True
            )  # Put on the item to cover with if it's not on already
        self.caller.location.msg_contents(
            "%s covers %s with %s." % (self.caller, to_cover.name, cover_with.name)
        )
        to_cover.db.covered_by = cover_with


class CmdUncover(MuxCommand):
    # JI (12/7/19) Since I'll be omitting cover for the time being, 
    # let's disable this command, too
    """
    Reveals a worn item of clothing that's currently covered up.

    Usage:
        uncover <obj>

    When you uncover an item of clothing, you allow it to appear in your
    description without having to take off the garment that's currently
    covering it. You can't uncover an item of clothing if the item covering
    it is also covered by something else.
    """

    key = "uncover"
    help_category = "clothing"

    def func(self):
        """
        This performs the actual command.
        """

        if not self.args:
            self.caller.msg("Usage: uncover <worn clothing object>")
            return

        to_uncover = self.caller.search(self.args, candidates=self.caller.contents)
        if not to_uncover:
            return
        if not to_uncover.db.geritur:
            self.caller.msg("You're not wearing %s!" % to_uncover.name)
            return
        if not to_uncover.db.covered_by:
            self.caller.msg("%s isn't covered by anything!" % to_uncover.name)
            return
        covered_by = to_uncover.db.covered_by
        if covered_by.db.covered_by:
            self.caller.msg("%s is under too many layers to uncover." % (to_uncover.name))
            return
        self.caller.location.msg_contents("%s uncovers %s." % (self.caller, to_uncover.name))
        to_uncover.db.covered_by = None

class Habeō(MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv

    Shows your inventory.
    """

    # Alternate version of the inventory command which separates
    # worn and carried items.

    key = "habeō"
    aliases = ['habeo']
    locks = "cmd:all()"
    arg_regex = r"$"
    help_category = 'Iussa Latīna'

    def func(self):
        """check inventory"""
        if not self.caller.contents:
            # JI (12/7/19) Adapted to Latin
            self.caller.msg("Tū rēs neque habēs neque geris.")
            return

        items = self.caller.contents

        carry_table = evtable.EvTable(border="header")
        wear_table = evtable.EvTable(border="header")
        for item in items:
            if not item.db.geritur:
                if item.db.is_burning:
                    glowing = f"|y(ard{'ēns' if item.db.sexus == 'neutrum' else 'entem'})|n |C{item.db.formae['acc_sg'][0]}|n"
                    carry_table.add_row(f"{ardēns} {'(dextrā)' if item.db.tenētur == 'dextrā' else '(sinistrā)'} {item.db.desc or ''}")
                else:
                    carry_table.add_row("|C%s|n" % item.db.formae['acc_sg'][0], '(dextrā)' if item.db.tenētur == 'dextrā' else '(sinistrā)', item.db.desc or "")
        if carry_table.nrows == 0:
            carry_table.add_row("|CNihil.|n", "")
        string = "|wTenēs:\n%s" % carry_table
        for item in items:
            if item.db.geritur:
                wear_table.add_row("|C%s|n" % item.db.formae['acc_sg'][0], item.db.desc or "")
        if wear_table.nrows == 0:
            wear_table.add_row("|CNihil.|n", "")
        string += "|/|wGeris:\n%s" % wear_table
        self.caller.msg(string)

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
        if latin_target and latin_caller:
            if target.db.geritur:
                target.remove(caller)
                # The below messages are currently delivered by remove()
#                caller.msg(f"{target_acc_sg} exuistī.")
#                caller.location.msg_contents(f"{caller.key} {target_acc_sg} exuit.", exclude=caller)

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
            if target.db.geritur:
                target.remove(caller,quiet=False)
            if target.db.tenētur:
                # New helper function to manage occupied hands
                take_out_of_hand(caller,target)

            # Lighten the callers toll_fer['ferēns']
            target_mass = target.db.physical['massa']
            caller.db.toll_fer['ferēns'] -= target_mass

        # Move object to caller's location
        target.move_to(caller.location, quiet=True)
        caller.msg(f"{target_direct_object_name} relīquistī.")
        caller.location.msg_contents(f"{caller.name} {target_direct_object_name} relīquit.", exclude=caller)

        # call the object script's at_drop() method.
        target.at_drop(caller)


class VestītaPersōnaCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for clothing, including new versions of 'give' and 'drop'
    that take worn and covered clothing into account, as well as a new
    version of 'inventory' that differentiates between carried and worn
    items.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(Indue())
        self.add(Exue())
#        self.add(CmdCover())
#        self.add(CmdUncover())
        self.add(Da())
        self.add(Relinque())
        self.add(Habeō())


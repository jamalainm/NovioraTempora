"""
Iānua

Based on Griatch's 'SimpleDoor'

This is a two-way exit representing a door that can be opened and
closed. The exit name will still show direction but you will need
to interact with the name of the door, which will be revealed by
looking in the exit's direction or from room descriptions.

Like Griatch's door, this will not work for a superuser.

"""

from evennia import default_cmds
from typeclasses.exitūs import Exitus
from evennia.utils.utils import inherits_from
from evennia.utils import create

from utils.latin_language.adjective_agreement import us_a_um
from utils.latin_language.decline_noun import DeclineNoun
from utils.latin_language.check_grammar import check_case

from unidecode import unidecode

class Iānua(Exitus):
    """
    A two-way exit "door" with some methods for affecting both "sides"
    of the door at the same time. For example, set a lock on either of
    the two sides using 'exitname.setlock("traverse:false()")'

    """

    def at_object_creation(self):
        """
        Called the very first time the door is created.

        """
        self.db.return_exit = None
        
    # add all of the case endings to attributes
    def basetype_posthook_setup(self):

        # Identify as closed door
        self.db.closed = False

        # add all of the case endings to attributes

        nominative = self.db.formae['nom_sg'][0]
        genitive = self.db.formae['gen_sg'][0]
        sexus = self.db.sexus

        word = DeclineNoun(nom=nominative, gen=genitive, gender=sexus)
        forms = word.make_paradigm()

        for key, value in forms.items():
            if key in self.db.formae:
                if value not in self.db.formae[key]:
                    self.db.formae[key].append(value)
            else:
                self.db.formae.update({key: [value]})

        self.db.Latin = True
        self.aliases.add(unidecode(self.key))
#        self.setdesc(nominative)



    def setlock(self, lockstring):
        """
        Sets identical locks on both sides of the door.

        Args:
            lockstring (str): A lockstring, like '"traverse:true()"'.

        """
        self.locks.add(lockstring)
        self.db.return_exit.locks.add(lockstring)

    def setdesc(self, description):
        """
        Sets identical descs on both sides of the door.

        Args:
            setdesc (str): a description

        """
        self.db.desc = description
        self.db.return_exit.db.desc = description

    def delete(self):
        """
        Deletes both sides of the door.

        """
        # we have to be careful to avoid a delete-loop.
        if self.db.return_exit:
            super().delete()
        super().delete()
        return True

    def at_failed_traverse(self, traversing_object):
        """
        Called when door traverse: lock fails.

        Args:
            traversing_object (Typeclassed entity): The object
                attempting the traversal

        """
        traversing_object.msg(f"{self.db.formae['nom_sg'][0]} claus{us_a_um('nom_sg',self.db.sexus)} est")

class Aperiātur(default_cmds.ObjManipCommand):
    """
    open a new exit from the current room but with Latin!

    Usage:
      open <door name>, <door genitive>, <door gender>, <destination> = <exit_name>, <direction thence>

    Handles the creation of exits. If a destination is given, the exit
    will point there. The <return exit> argument sets up an exit at the
    destination leading back to the current room. Destination name
    can be given both as a #dbref and a name, if that name is globally
    unique.

    """

    key = "aperiātur"
    locks = "cmd:perm(open) or perm(Builder)"
    help_category = "Building"

    new_obj_lockstring = "control:id({id}) or perm(Admin);delete:id({id}) or perm(Admin)"
    # a custom member method to chug out exits and do checks
    def create_exit(self, exit_name=None, location=None, destination=None, exit_aliases=None, typeclass=None, door_name=None, door_genitive=None, door_gender=None, return_exit_name=None):
        """
        Helper function to avoid code duplication.
        At this point we know destination is a valid location

        """
        caller = self.caller
        string = ""
        # check if this exit object already exists at the location.
        # we need to ignore errors (so no automatic feedback)since we
        # have to know the result of the search to decide what to do.
        exit_obj = caller.search(exit_name, location=location, quiet=True, exact=True)
        if len(exit_obj) > 1:
            # give error message and return
            caller.search(exit_name, location=location, exact=True)
            return None
        if exit_obj:
            exit_obj = exit_obj[0]
            if not exit_obj.destination:
                # we are trying to link a non-exit
                string = "'%s' iam est neque exitus est!\nSī vīs mutāre in "
                string += (
                    "exitum, 'fīnis' quīdam reī prius dandus est."
                )
                caller.msg(string % exit_name)
                return None
            # we are re-linking an old exit.
            old_destination = exit_obj.destination
            if old_destination:
                string = "Exitus %s iam est." % exit_name
                if old_destination.id != destination.id:
                    # reroute the old exit.
                    exit_obj.destination = destination
                    if exit_aliases:
                        [exit_obj.aliases.add(alias) for alias in exit_aliases]
                    string += " Iter nōn iam '%s' dūcit sed '%s' agnōminibus mutātīs." % (
                        old_destination.name,
                        destination.name,
                    )
                else:
                    string += " Iam ad fīnem optātum dūcit."

        else:
            # exit does not exist before. Create a new one.
            lockstring = self.new_obj_lockstring.format(id=caller.id)
            typeclass = Iānua
            exit_obj = create.create_object(
                typeclass=typeclass,
                key=exit_name,
                location=location,
                aliases=exit_aliases,
                locks=lockstring,
                report_to=caller,
                attributes=[
                    ("formae",{"nom_sg":[door_name],"gen_sg":[door_genitive]}),
                    ("sexus",door_gender),
                    ]
            )
            if exit_obj:
                # storing a destination is what makes it an exit!
                exit_obj.destination = destination
                string = (
                    ""
                    if not exit_aliases
                    else " (aliases: %s)" % (", ".join([str(e) for e in exit_aliases]))
                )
                string = "Exitus novus '%s' factus est ab %s ad %s%s." % (
                    exit_name,
                    location.db.formae['abl_sg'][0],
                    destination.name,
                    string,
                )
            else:
                string = "Error: Exitus '%s' nōn factus est." % exit_name

            back_obj = create.create_object(
                    typeclass=typeclass,
                    key=return_exit_name,
                    location = destination,
                    aliases=exit_aliases,
                    locks=lockstring,
                    report_to=caller,
                    attributes=[
                        ("formae",{"nom_sg":[door_name],"gen_sg":[door_genitive]}),
                        ("sexus",door_gender),
                    ]
            )
            if back_obj:
                # storing a destination is what makes it an exit!
                back_obj.destination = location
                exit_obj.db.return_exit = back_obj
                back_obj.db.return_exit = exit_obj
                string = (
                    ""
                    if not exit_aliases
                    else " (aliases: %s)" % (", ".join([str(e) for e in exit_aliases]))
                )
                string = "Reditus novus '%s' factus est ab %s ad %s%s." % (
                    return_exit_name,
                    destination.db.formae['abl_sg'][0],
                    location.name,
                    string,
                )

                exit_obj.setdesc(exit_obj.db.formae['nom_sg'][0])
            else:
                string = "Error: Reditus '%s' nōn factus est." % exit_name


        # emit results
        caller.msg(string)
        return exit_obj

    def func(self):
        """
        This is where the processing starts.
        Uses the ObjManipCommand.parser() for pre-processing
        as well as the self.create_exit() method.
        """
        caller = self.caller

        if not self.args or not self.rhs or len(self.lhslist) != 4 or len(self.rhslist) != 2:
            string = "Usage: aperiātur <door name> <door genitive> <door gender> <destination> = <direction hence> <direction thence> "
            caller.msg(string)
            return

        # We must have a location to open an exit
        location = caller.location
        if not location:
            caller.msg("You cannot create an exit from a None-location.")
            return

        # obtain needed info from cmdline

        door_name = self.lhslist[0]
        door_genitive = self.lhslist[1]
        door_gender = self.lhslist[2]

        if door_gender not in ['māre', 'muliebre', 'neutrum']:
            caller.msg("Quod sexus est?")
            return

        exit_name = self.rhslist[0]
        return_exit_name = self.rhslist[-1]
#        exit_aliases = self.lhs_objs[0]["aliases"]
#        exit_typeclass = self.lhs_objs[0]["option"]
        dest_name = self.lhslist[-1]

        # first, check so the destination exists.
        destination = caller.search(dest_name, global_search=True)
        if not destination:
            return

        # Create exit
        ok = self.create_exit(exit_name=exit_name, location=location, destination=destination, door_name=door_name, door_genitive=door_genitive, door_gender=door_gender, typeclass=Iānua, return_exit_name=return_exit_name)
        if not ok:
            # an error; the exit was not created, so we quit.
            return

class AperīClaudeIānuam(default_cmds.MuxCommand):
    """
    Open and close a door

    Usage:
        aperī <iānuam> [in quandam partem]
        claude <iānuam> [in quandam partem]

    """

    key = 'aperī'
    aliases = ['aperi','claude']
    locks = "cmd:all()"
    help_category = "Iussa Latīna"

    def func(self):
        "implements the door functionality"
        caller = self.caller

        location = caller.location
        
        exits = [o for o in location.contents if o.location is location and o.destination]

        doors = [
                o for o in exits if o.is_typeclass('typeclasses.iānuae.Iānua', exact=False)
                ]

        intended_door = None

        intended_direction = None

        if not self.args:
            caller.msg("Ūsus: aperī||claude <iānuam> [in quandam partem]")
            return

        if len(doors) < 1:
            caller.msg("Nihil est quod aperīrī possit.")
            return
        elif len(doors) == 1:
            intended_direction = doors[0]

        if len(self.arglist) == 1:
            intended_door = self.arglist[0]
        else:
            for o in exits:
                if unidecode(o.key) in unidecode(self.args):
                    intended_direction = o
                    intended_door = unidecode(self.args).replace(unidecode(o.key),'')
                    intended_door = intended_door.strip()

        if not intended_direction or not intended_door:
            caller.msg("Quid in quam partem aperīre vīs?")
            return


        # Check that direction and door match
        if intended_direction not in doors:
            caller.msg("Nihil est quod in eam partem aperīrī possit.")
            return
        door = intended_direction
        
        # check grammar

        if check_case(caller, door, intended_door, 'acc_sg') == False:
            return

        return_exit = door.db.return_exit

        # Open door
        if unidecode(self.cmdstring) == 'aperi':
#            if door.locks.check(self.caller, "traverse"):
            if door.db.closed == False:
                self.caller.msg(f"{door.db.formae['nom_sg'][0]} iam apert{us_a_um('nom_sg',door.db.sexus)} est")
                return
            else:
                door.setlock("traverse:true()")
                self.caller.msg(f"{door.db.formae['acc_sg'][0]} aperuistī.")
                door.db.closed = False
                door.location.msg_contents(
                        f"{door.db.formae['nom_sg'][0]} {door.key} ab {caller.db.formae['abl_sg'][0]} apert{us_a_um('nom_sg',door.db.sexus)} est.",
                        exclude=caller
                        )
                return_exit.db.closed = False
                return_exit.location.msg_contents(
                        f"{return_exit.db.formae['nom_sg'][0]} {return_exit.key} apert{us_a_um('nom_sg',return_exit.db.sexus)} est."
                        )
                door.setdesc(f"{door.db.formae['nom_sg'][0]} apert{us_a_um('nom_sg',door.db.sexus)}")
        # Close door
        else: # close
#            if not door.locks.check(self.caller, "traverse"):
            if door.db.closed == True:
                self.caller.msg(f"{door.db.formae['nom_sg'][0]} iam claus{us_a_um('nom_sg',door.db.sexus)} est")
                return
            else:
                door.setlock("traverse:false()")
                self.caller.msg(f"{door.db.formae['acc_sg'][0]} clausistī.")
                door.db.closed = True
                door.location.msg_contents(
                        f"{door.db.formae['nom_sg'][0]} {door.key} ab {caller.db.formae['abl_sg'][0]} claus{us_a_um('nom_sg',door.db.sexus)} est.",
                        exclude=caller
                        )
                return_exit.db.closed = True
                return_exit.location.msg_contents(
                        f"{return_exit.db.formae['nom_sg'][0]} {return_exit.key} claus{us_a_um('nom_sg',return_exit.db.sexus)} est."
                        )
                door.setdesc(f"{door.db.formae['nom_sg'][0]} claus{us_a_um('nom_sg',door.db.sexus)}")

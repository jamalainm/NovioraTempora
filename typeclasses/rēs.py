"""
In order to make proper use of the Rēs typeclass, at object creation
the following must be specified:
    1) a nominative singular form for the noun
    2) a genitive singular form for the noun
    3) a grammatical gender for the noun

"""
# from typeclasses.inflected_noun import InflectedNoun
#from evennia import DefaultObject
from collections import defaultdict
from evennia.contrib.ingame_python.typeclasses import EventObject
from utils.latin_language.populate_forms import populate_forms

from evennia.contrib.ingame_python.utils import register_events

from utils.latin_language.list_to_string import list_to_string
from utils.latin_language.get_numbered_name import get_numbered_name

# from commands.iussa_rērum import LigātūraCmdSet
# from commands.default_cmdsets import LigātūraCmdSet

class Rēs(EventObject):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, account=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_before_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_traverse(traversing_object, source_loc) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_after_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

     """

    def basetype_posthook_setup(self):

        # add all of the case endings to attributes
        if hasattr(self, 'db'):
            if self.db.formae:
                if len(self.db.formae['nom_sg']) > 1:
                    nōmen_nom = self.db.formae['nom_sg'][1]
                    nōmen_gen = self.db.formae['gen_sg'][1]


                nominative = self.db.formae['nom_sg'][0]
                genitive = self.db.formae['gen_sg'][0]
                sexus = self.db.sexus

                populate_forms(self, nom=nominative, gen=genitive, gender=sexus)

                # Check if there is a nōmen for this character
                if len(self.db.formae['nom_sg']) > 1:

                    populate_forms(self, nom=nōmen_nom, gen=nōmen_gen, gender=sexus)

                self.db.Latin = True

    def return_appearance(self, looker, **kwargs):
        """
        # Lightly editing to change "You see" to "Ecce"
        # and 'Exits' to 'Ad hos locos ire potes:'
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """


        if not looker:
            return ""

        # If it's dark, they can't see
        if looker.location.db.āter:
            lūx = False
            contents = looker.contents + looker.location.contents
            for con in contents:
                if con.db.ardēns == True:
                    lūx = True

            if lūx == False:
                looker.msg("Nihil per tenebrās vidēre potes.")
                return

        # get and identify all objects
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        colorful_exits = []
        # adjusted the exit name to take out the dbref so builders can
        # click on the exits to go there
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(con.key)
                if con.is_typeclass("typeclasses.iānuae.Iānua",exact=False):
                    if con.db.closed == True:
                        colorful_exits.append(f"|lc{con.key}|lt|g[{con.key}]|n|le")
                    else:
                        colorful_exits.append(f"|lc{con.key}|lt|g{con.key}|n|le")
                else:
                    colorful_exits.append(f"|lc{con.key}|lt|g{con.key}|n|le")
            elif con.has_account:
                if con.db.ardēns:
                    users.append("|y(ardēns)|n |c%s|n" % key)
                else:
                    users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)

        # get description, build string
        string = "\n|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc

        if desc:
            string += "%s\n" % desc

        if exits:
            # Changing this string so that exits appear green
            # string += "\n|wAd hos locos potes ire:|n\n " + LatinNoun.list_to_string(exits)
#            colorful_exits = []
#            for exit in exits:
#                colorful_exits.append(f"|lc{exit}|lt|g{exit}|n|le")
            colorful_exits = sorted(colorful_exits)
            string += "\n|wAd hōs locōs īre licet:|n\n " + list_to_string(colorful_exits) + "\n"
        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
#                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                    key, _ = get_numbered_name(itemlist[0], nitem, looker, key=key)
                    if itemlist[0].db.ardēns:
                        key = "|y(ardēns)|n " + key
#                    if itemlist[0].db.descriptive_name:
                    if itemlist[0].db.vīsus:
#                        key = itemlist[0].db.descriptive_name
                        key = itemlist[0].db.vīsus
                else:
#                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                    key = [get_numbered_name(item, nitem, looker, key=key)[1] for item in itemlist][
                        0
                    ]
                thing_strings.append(key)

            string += "\n|wEcce:|n\n " + list_to_string(users + thing_strings)

        return string


#    def at_get(getter):
#        mass = 0
#        if hasattr(self, 'db'):
#            if self.db.physical:
#                if self.db.physical['massa']:
#                    mass = self.db.physical['massa']
#
#        if hasattr(getter, 'db'):
#            if getter.db.toll_fer and self.db.physical:
#                getter.db.toll_fer['ferēns'] += mass
#

# EVENT_LIGĀ = """
#     A character holding the leash (lōrum) can tie the leash to certain
#     other objects. A tied character can't go when the leash is held
#     and must follow when someone holding the leash exits.
# 
#     variables you can use in this event:
#         character: the character holding the leash
#         target: the character to which the leash is tied
#         ligature: the thing that can connect
# """

class Ligātūra(Rēs):

#    _events = {
#            "ligā": (['character','target','ligature'],EVENT_LIGĀ),
#            }

    pass

#     def at_object_creation(self):
#         self.cmdset.add(LigātūraCmdSet(), permanent=True)

class Inflammābilis(Rēs):

    def at_object_creation(self):

        self.db.inflammābilis = True
        self.db.ardēns = True

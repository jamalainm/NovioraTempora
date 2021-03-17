"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
# from evennia import DefaultCharacter
from evennia.contrib.ingame_python.typeclasses import EventCharacter
from world.tb_basic import TBBasicCharacter

from evennia.utils.utils import inherits_from

from commands import default_cmdsets
from typeclasses import vestīmenta

from utils.latin_language.populate_forms import populate_forms
from utils.latin_language.list_to_string import list_to_string
from utils.latin_language.adjective_agreement import us_a_um

import random

# class Persōna(DefaultCharacter,InflectedNoun):
class Persōna(EventCharacter,TBBasicCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    def at_object_creation(self):
        self.cmdset.add_default(default_cmdsets.PersōnaCmdSet, permanent=True)

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

                # assign handedness
                if random.random() >= 0.9:
                    self.db.handedness = 'sinistrā'
                else:
                    self.db.handedness = 'dextrā'

                # Set 'manibus_plēnīs' and 'manibus_vacuīs'
                self.db.manibus_plēnīs = []
                self.db.manibus_vacuīs = ['dextrā','sinistrā']

                # Set stats if not already given
                if not self.db.ingenia:
                    statNums = [0,0,0,0,0,0]
                    points = 27
                    while points > 0:
                        index = random.randint(0,5)
                        if statNums[index] < 5 and points > 0:
                            statNums[index] += 1
                            points -= 1
                        elif statNums[index] in [5, 6] and points > 1:
                            statNums[index] += 1
                            points -= 2
                    for index, value in enumerate(statNums):
                        statNums[index] += 9

                    self.db.ingenia = {'vīrēs':statNums[0], 'pernīcitās':statNums[1],'valētūdō':statNums[2],'ratiō':statNums[3],'sapientia':statNums[4],'grātia':statNums[5]}

                # Set 'puncta valētūdinis' (health points)
                bonus = self.db.ingenia['valētūdō']
                bonus = (bonus - 11) if bonus % 2 else (bonus - 10)
                max_pv = (10 + bonus) if (10 + bonus) > 0 else 1
                self.db.pv = {'max': max_pv, "nunc": max_pv}

                # Set carrying capacity
                strength = self.db.ingenia['vīrēs']
                self.db.toll_fer = {
                        'tollere': round(strength * 30 * 0.45, 1),
                        'impedīta': round(strength * 5 * 0.45, 1),
                        'impedītissima': round(strength * 10 * 0.45, 1),
                        'ferēns': 0,
                        'max': round(strength * 15 * 0.45, 1)
                        }

            else:
                pass
        else:
            pass

    def at_say(
        self,
        message,
        msg_self=None,
        msg_location=None,
        receivers=None,
        msg_receivers=None,
        **kwargs,
    ):
        """
        Display the actual say (or whisper) of self.

        This hook should display the actual say/whisper of the object in its
        location.  It should both alert the object (self) and its
        location that some text is spoken.  The overriding of messages or
        `mapping` allows for simple customization of the hook without
        re-writing it completely.

        Args:
            message (str): The message to convey.
            msg_self (bool or str, optional): If boolean True, echo `message` to self. If a string,
                return that message. If False or unset, don't echo to self.
            msg_location (str, optional): The message to echo to self's location.
            receivers (Object or iterable, optional): An eventual receiver or receivers of the message
                (by default only used by whispers).
            msg_receivers(str): Specific message to pass to the receiver(s). This will parsed
                with the {receiver} placeholder replaced with the given receiver.
        Keyword Args:
            whisper (bool): If this is a whisper rather than a say. Kwargs
                can be used by other verbal commands in a similar way.
            mapping (dict): Pass an additional mapping to the message.

        Notes:


            Messages can contain {} markers. These are substituted against the values
            passed in the `mapping` argument.

                msg_self = 'You say: "{speech}"'
                msg_location = '{object} says: "{speech}"'
                msg_receivers = '{object} whispers: "{speech}"'

            Supported markers by default:
                {self}: text to self-reference with (default 'You')
                {speech}: the text spoken/whispered by self.
                {object}: the object speaking.
                {receiver}: replaced with a single receiver only for strings meant for a specific
                    receiver (otherwise 'None').
                {all_receivers}: comma-separated list of all receivers,
                                 if more than one, otherwise same as receiver
                {location}: the location where object is.

        """
        msg_type = "say"
        if kwargs.get("whisper", False):
            # whisper mode
            msg_type = "whisper"
            msg_self = (
                '{self} whisper to {all_receivers}, "|n{speech}|n"'
                if msg_self is True
                else msg_self
            )
            msg_receivers = msg_receivers or '{object} whispers: "|n{speech}|n"'
            msg_location = None
        else:
            # split "message" into two parts if possible
            two_part_speech = False
            speech_list = message.split(' ')
            speech_one = speech_list[0]
            speech_two = ""
            if len(speech_list) > 1:
                speech_two = (' ').join(speech_list[1:])
                two_part_speech = True

            if two_part_speech:
                msg_self = '"|n{speech_one}|n" inquis "|n{speech_two}|n"'
                msg_location = '{object} "|n{speech_one}|n" inquit "|n{speech_two}|n"'
                msg_receivers = '{object} tibi "|n{speech_one}|n" inquit "|n{speech_two}|n"'
            else:
                msg_self = '"|n{speech_one}|n" inquis.'
                msg_location = '{object} "|n{speech_one}|n" inquit.'
                msg_receivers = '{object} tibi "|n{speech_one}|n" inquit.'

        custom_mapping = kwargs.get("mapping", {})
        receivers = make_iter(receivers) if receivers else None
        location = self.location

        if msg_self:
            self_mapping = {
                "self": "You",
                "object": self.get_display_name(self),
                "location": location.get_display_name(self) if location else None,
                "receiver": None,
                "all_receivers": ", ".join(recv.get_display_name(self) for recv in receivers)
                if receivers
                else None,
                "speech_one": speech_one,
                "speech_two": speech_two,
            }
            self_mapping.update(custom_mapping)
            self.msg(text=(msg_self.format(**self_mapping), {"type": msg_type}), from_obj=self)

        if receivers and msg_receivers:
            receiver_mapping = {
                "self": "You",
                "object": None,
                "location": None,
                "receiver": None,
                "all_receivers": None,
                "speech": message,
            }
            for receiver in make_iter(receivers):
                individual_mapping = {
                    "object": self.get_display_name(receiver),
                    "location": location.get_display_name(receiver),
                    "receiver": receiver.get_display_name(receiver),
                    "all_receivers": ", ".join(recv.get_display_name(recv) for recv in receivers)
                    if receivers
                    else None,
                }
                receiver_mapping.update(individual_mapping)
                receiver_mapping.update(custom_mapping)
                receiver.msg(
                    text=(msg_receivers.format(**receiver_mapping), {"type": msg_type}),
                    from_obj=self,
                )

        if self.location and msg_location:
            location_mapping = {
                "self": "You",
                "object": self,
                "location": location,
                "all_receivers": ", ".join(str(recv) for recv in receivers) if receivers else None,
                "receiver": None,
                "speech_one": speech_one,
                "speech_two": speech_two,
            }
            location_mapping.update(custom_mapping)
            exclude = []
            if msg_self:
                exclude.append(self)
            if receivers:
                exclude.extend(receivers)
            self.location.msg_contents(
                text=(msg_location, {"type": msg_type}),
                from_obj=self,
                exclude=exclude,
                mapping=location_mapping,
            )

    def at_after_move(self,source_location):
        super().at_after_move(source_location)

        if self.db.pv:
            prompt = f"|wVīta: {self.db.pv['nunc']}/{self.db.pv['max']}"

            self.msg(prompt)

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

            # get description, build string
            string = "|c%s|n\n" % self.get_display_name(looker)
            desc = self.db.desc

            # JI (12/7/9) Adding the following lines to accommodate clothing
            worn_string_list = []
            clothes_list = vestīmenta.get_worn_clothes(self, exclude_covered=True)

            # Append worn, uncovered clothing to the description
            for garment in clothes_list:

                # if 'worn' is True, just append the name
                if garment.db.geritur is True:
                    if garment.db.ardēns:
                        worn_string_list.append(f"|yarden{'s' if garment.db.sexus == 'neutrum' else 'tem'}|n {garment.db.acc_sg[0]}")

                    # JI (12/7/19) append the accusative name to the description,
                    # since these will be direct objects
                    else:
                        worn_string_list.append(garment.db.formae['acc_sg'][0])
                        
                # Otherwise, append the name and the string value of 'worn'
                elif garment.db.geritur:
                    worn_string_list.append("%s %s" % (garment.name, garment.db.geritur))

            # get held clothes
            possessions = self.contents
            held_list = []
            for possession in possessions:
                if possession.db.tenētur:
                    if possession.db.ardēns:
                        held_list.append(f"|y(arden{'s' if possession.db.sexus == 'neutrum' else 'tem'})|n {possession.db.formae['acc_sg'][0]}")
                    else:
                        held_list.append(possession.db.formae['acc_sg'][0])
            if desc:
                string += f"{self.db.desc}"
            # Append held items.
            if held_list:
                string += "\n\n" + f"tenet: {list_to_string(held_list)}."
            # Append worn clothes.
            if worn_string_list:
                string += "\n\n" + f"gerit: {list_to_string(worn_string_list)}."
            else:
#                string += "|/|/%s nūd%s est!" % (self, us_a_um('nom_sg',self.db.sexus))
                string += "\n\n" + f"{self.key} nūd{us_a_um('nom_sg',self.db.sexus)} est!"
            return string

    def announce_move_from(self, destination, msg=None, mapping=None):
            """
            Called if the move is to be announced. This is
            called while we are still standing in the old
            location.
            Args:
                destination (Object): The place we are going to.
                msg (str, optional): a replacement message.
                mapping (dict, optional): additional mapping objects.
            You can override this method and call its parent with a
            message to simply change the default message.  In the string,
            you can use the following as mappings (between braces):
                object: the object which is moving.
                exit: the exit from which the object is moving (if found).
                origin: the location of the object before the move.
                destination: the location of the object after moving.
            """
            if not self.location:
                return

            # changing {origin} to {exit}
            string = msg or "{object} {exit} discessit." #, heading for {destination}."

            # Get the exit from location to destination
            location = self.location
            exits = [
                o for o in location.contents if o.location is location and o.destination is destination
            ]
            mapping = mapping or {}
            mapping.update({"character": self})

            # No event typeclasses currently in use 3/6/21
#            if exits:
#                exits[0].callbacks.call(
#                    "msg_leave", self, exits[0], location, destination, string, mapping
#                )
#                string = exits[0].callbacks.get_variable("message")
#                mapping = exits[0].callbacks.get_variable("mapping")

            # If there's no string, don't display anything
            # It can happen if the "message" variable in events is set to None
            if not string:
                return

            super().announce_move_from(destination, msg=string, mapping=mapping)

    def announce_move_to(self, source_location, msg=None, mapping=None):
        """
        Called after the move if the move was not quiet. At this point
        we are standing in the new location.
        Args:
            source_location (Object): The place we came from
            msg (str, optional): the replacement message if location.
            mapping (dict, optional): additional mapping objects.
        You can override this method and call its parent with a
        message to simply change the default message.  In the string,
        you can use the following as mappings (between braces):
            object: the object which is moving.
            exit: the exit from which the object is moving (if found).
            origin: the location of the object before the move.
            destination: the location of the object after moving.
        """

        if not source_location and self.location.has_account:
            # This was created from nowhere and added to an account's
            # inventory; it's probably the result of a create command.
            string = "%s nunc tuīs in manibus." % self.get_display_name(self.location)
            self.location.msg(string)
            return

        # added the line below because
        origin = source_location
        # error checking
        self.location.msg(source_location)
        if source_location:
            origin = source_location.db.formae['abl_sg'][0]
            string = msg or f"{self.key} ab {source_location.db.formae['abl_sg'][0]} vēnit."
        else:
            string = "{character} vēnit."

        # adding '.db.abl_sg' to end of 'source_location' and moving from line below
        # up into the 'if source_location' conditional
        destination = self.location
        exits = []
        mapping = mapping or {}
        mapping.update({"character": self})

        if origin:
            exits = [
                o
                for o in destination.contents
                if o.location is destination and o.destination is origin
            ]
            # No event typeclasses currently installed 3/6/21
#            if exits:
#                exits[0].callbacks.call(
#                    "msg_arrive", self, exits[0], origin, destination, string, mapping
#                )
#                string = exits[0].callbacks.get_variable("message")
#                mapping = exits[0].callbacks.get_variable("mapping")

        # If there's no string, don't display anything
        # It can happen if the "message" variable in events is set to None
        if not string:
            return

        super().announce_move_to(source_location, msg=string, mapping=mapping)

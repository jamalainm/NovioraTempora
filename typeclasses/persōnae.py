"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter

from typeclasses.inflected_noun import InflectedNoun
from commands import default_cmdsets
from utils.latin_language.populate_forms import populate_forms

import random

# class Persōna(DefaultCharacter,InflectedNoun):
class Persōna(DefaultCharacter):
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

                populate_forms(self, nominative, genitive, sexus)

                # Check if there is a nōmen for this character
                if len(self.db.formae['nom_sg']) > 1:

                    populate_forms(self, nōmen_nom, nōmen_gen, sexus)

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


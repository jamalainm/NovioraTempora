# file mygame/utils/latin_language/get_numbered_name.py

from evennia.utils import ansi

def get_numbered_name(self, count, looker, **kwargs):
    """
    Return the numbered (singular / plural) forms of this object's key.
    This is by default called by return appearance and is used for 
    grouping multiple same-named of this object. Note that this will 
    be called on *every* member of a group even though the plural name
    will be only shown once. Also the singular display version, such as
    'an apple', 'a tree' is determined from this method.

    Args:
        count (int): Number of objects of this type
        looker (Object): onlooker. Not used by default
    Kwargs:
        key (str): optional key to pluralize, if given, use this instead
        of the object's key
    Returns:
        singular (str): the singular form to display
        plural (str): the determined plural form of the key, including count.
    """
    key = kwargs.get("key", self.key)
    key = ansi.ANSIString(key) # Needed to allow inflection of colored names
    if self.db.formae:
        plural = self.db.formae['nom_pl'][0]
    else:
        plural = self.key

    plural = f"{count} {plural}"

    singular = self.key

    if not self.aliases.get(plural, category="plural_key"):
        # We need to wipe any old plurals/an/a in case key changed in the interim
        self.aliases.clear(category="plural_key")
        self.aliases.add(plural, category="plural_key")

        # save teh singular form as an aliases here too so we can display "an egg"
        # and also look at "an egg"
        self.aliases.add(singular, category="plural_key")
        
    return singular, plural

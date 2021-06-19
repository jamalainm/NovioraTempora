# mygame/tempora.py

import evennia
from evennia.utils import gametime
from typeclasses.locī import Locus

def prīmā_lūce():
    """ When the sun rises, display a message in every room. """
    # Browse all rooms
    for locus in Locus.objects.all():
        locus.msg_contents("|ySōl orītur.|n")

    # Set "dark" = False for external rooms
    externa = evennia.search_tag("forīs", category="zōna")
    for e in externa:
        e.db.āter=False

def incipe_sōlem_orīrī():
    """ schedule a sunrise event to happen every day at 6 AM """
    script = gametime.schedule(prīmā_lūce, repeat=True, hour=6, min=0, sec=0)
    script.key = "prīmā lūce"

def occāsū():
    """ When the sun sets, display a message in every room. """
    # Browse all rooms
    for locus in Locus.objects.all():
        locus.msg_contents("|rSōl occidit.|n")

    # Set "dark" = True for external rooms
    externa = evennia.search_tag("forīs", category="zōnā")
    for e in externa:
        e.db.āter=True


def incipe_sōlem_occidere():
    """ schedule a sunset event to happen every day at 6 PM """
    script = gametime.schedule(occāsū, repeat=True, hour=18, min=0, sec=0)
    script.key = "occāsū"


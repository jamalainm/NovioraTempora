# file /mygame/utils/latin/check_grammar.py

from unidecode import unidecode

def check_case(caller, obj, intended_target, case):
    """ Notify the caller if the target was found but the wrong case was specified """

    lower_case = [x.lower() for x in obj.db.formae[case]]
    unidecoded_lower_case = [unidecode(x) for x in lower_case]
    lower_case += unidecoded_lower_case
    if intended_target.strip().lower() not in lower_case:
        caller.msg(f"(Did you mean '{obj.db.formae[case][0]}'?)")
        return False

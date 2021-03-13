# file /mygame/utils/latin/check_grammar.py

def check_case(caller, obj, intended_target, case):
    """ Notify the caller if the target was found but the wrong case was specified """

    lower_case = [x.lower() for x in obj.db.formae[case]]
    if intended_target.strip().lower() not in lower_case:
        caller.msg(f"target: {obj.name}")
        caller.msg(f"intended_target: {intended_target}")
        caller.msg(f"(Did you mean '{obj.db.formae[case][0]}'?)")
        return False

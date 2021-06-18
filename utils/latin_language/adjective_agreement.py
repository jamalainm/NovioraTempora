# file mygame/utils/latin/adjective_agreement.py

from utils.latin_language.adjective_inflections import us_a_um_inflections

def us_a_um(case,gender):
    ending = us_a_um_inflections[case][gender]
    return ending

def us_a_um2(case,gender,noun=None):
    if noun:
        gender = noun.db.sexus
        if noun.db.formae['gen_sg'][0][-2:] == 'um':
            case = case[:-2] + 'pl'

    ending = us_a_um_inflections[case][gender]
    return ending


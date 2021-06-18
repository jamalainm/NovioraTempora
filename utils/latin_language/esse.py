# utils/latin_language/esse.py

def esse(noun):
    """ simple helper function to return 'est' or 'sunt,' accounting for always plurals """
    if noun.db.formae['gen_sg'][0][-2:] == 'um':
        return 'sunt'
    else:
        return 'est'

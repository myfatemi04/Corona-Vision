admin0_codes = {}
admin1_codes = {}
admin2_codes = {}

admin0_names = {}
admin1_names = {}
admin2_names = {}

def store_codes(a0, a1, a2, a0_c, a1_c, a2_c):
    if a0_c:
        admin0_codes[a0] = a0_c
        admin0_names[a0_c] = a0

    if a1_c:
        if a0 not in admin1_codes:
            admin1_codes[a0] = {}
        admin1_codes[a0][a1] = a1_c

        if a0 not in admin1_names:
            admin1_names[a0] = {}
        admin1_names[a0][a1_c] = a1

    if a2_c:
        if a0 not in admin2_codes:
            admin2_codes[a0] = {}
        if a1 not in admin2_codes[a0]:
            admin2_codes[a0][a1] = {}
        admin2_codes[a0][a1][a2] = a2_c

        if a0 not in admin2_names:
            admin2_names[a0] = {}
        if a1 not in admin2_names[a0]:
            admin2_names[a0][a1] = {}
        admin2_names[a0][a1][a2_c] = a2

# returns admin0_code, admin1_code, admin2_code
def get_codes(admin0, admin1, admin2):
    admin0_code = admin1_code = admin2_code = ''
    
    if admin0 in admin0_codes:
        admin0_code = admin0_codes[admin0]

    if admin0 in admin1_codes:
        if admin1 in admin1_codes[admin0]:
            admin1_code = admin1_codes[admin0][admin1]
            
    if admin0 in admin2_codes:
        if admin1 in admin2_codes[admin0]:
            if admin2 in admin2_codes[admin0][admin1]:
                admin2_code = admin2_codes[admin0][admin1][admin2]
    
    return admin0_code, admin1_code, admin2_code

# returns admin0_code, admin1_code, admin2_code
def get_admin0_name(admin0_code):
    if admin0_code in admin0_names:
        return admin0_names[admin0_code]

def get_admin1_name(admin0, admin1_code):
    if admin0 in admin1_names:
        if admin1_code in admin1_names[admin0]:
            return admin1_names[admin0][admin1_code]

def get_admin2_name(admin0, admin1, admin2_code):
    if admin0 in admin2_names:
        if admin1 in admin2_names[admin0]:
            if admin2_code in admin2_names[admin0][admin1]:
                return admin2_names[admin0][admin1][admin2_code]

def get_admin_level(admin0, admin1, admin2):
    if not admin0:
        return 'world'
    if not admin1:
        return 'admin0'
    if not admin2:
        return 'admin1'
    return 'admin2'


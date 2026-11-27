
RYX_MOVES = {
    # Standing normals
    "st_lp": (14, 3),
    "st_hp": (18, 2),
    "st_mk": (23, 5),

    # Crouching normals
    "cr_lp": (11, 1),
    "cr_mp": (11, 2),
    "cr_hp": (20, 4),
    "cr_lk": (14, 4),
    "cr_mk": (13, 1),
    "cr_hk": (13, 4),

    # Jumping normals
    "j_mp": (17, 1),
    "j_mk": (14, 1),
    "j_hk": (22, 1),

    # Hadoken
    "hadoken": (1, 1),

    # Ryusokyaku
    "ryusokyaku": (2, 1),
    "mk_ryusokyaku": (15, 1),
    "hk_ryusokyaku": (16, 2),
    "ex_ryusokyaku": (22, 8),

    # Tatsumaki
    "tatsu": (3, 1),
    "lk_tatsu": (15, 3),
    "hk_tatsu": (9, 2),
    "ex_tatsu": (18, 6),
    "air_tatsu": (10, 1),

    # Shoryuken
    "shoryuken": (4, 1),
    "lp_shoryuken": (16, 1),
    "hp_shoryuken": (20, 8),

    # Unique attacks
    "senbukyaku": (9, 1),
    "target_combo": (8, 1),

    # Focus attacks
    "focus_attack": (18, 1),
    "ex_focus_cancel": (13, 3),
    "ex_red_focus": (18, 4),

    # Super and Ultras
    "raging_demon": (5, 1),
    "metsu_hadoken": (6, 1),
    "messatsu_goshoryu": (7, 1),
}


# Custom move generator
def special_move(template, strength, text_id, input_id, action_ids):

    modifiers = {
        "light": "ID_CMD_CMN_0023",
        "medium": "ID_CMD_CMN_0024",
        "heavy": "ID_CMD_CMN_0025",
        "ex": "ID_CMD_CMN_0022"
    }

    modifier = modifiers[strength]

    return {
        "template": template,
        "strings": [
            "",
            modifier,
            f"ID_TU3_CMD_RYX_{text_id:04d}",
            "",
            "",
            modifier,
            f"ID_TU3_CMD_RYX_{input_id:04d}",
            ""
        ],
        "action_ids": action_ids
    }


RYX_CUSTOM_MOVES = {

    # Ryusokyaku - verified
    "lk_ryusokyaku": special_move(
        (15, 1), "light", 22, 23, [150]
    ),

    # Hadoken - experimental
    "lp_hadoken": special_move(
        (1, 1), "light", 10, 11, [100]
    ),

    "mp_hadoken": special_move(
        (1, 1), "medium", 10, 11, [101]
    ),

    "hp_hadoken": special_move(
        (1, 1), "heavy", 10, 11, [102]
    ),

    "ex_hadoken": special_move(
        (1, 1), "ex", 10, 11, [103]
    ),

    # Shoryuken - experimental
    "mp_shoryuken": special_move(
        (16, 1), "medium", 14, 15, [119, 120]
    ),

    # Tatsumaki - experimental
    "mk_tatsu": special_move(
        (15, 3), "medium", 16, 17, [161, 162]
    ),
}

def normal_move(template, stance, strength, attack, action_ids):

    stances = {
        "standing": "ID_CMD_CMN_0003",
        "crouching": "ID_CMD_CMN_0004",
        "jumping": "ID_CMD_CMN_0005"
    }

    strengths = {
        "light": "ID_CMD_CMN_0023",
        "medium": "ID_CMD_CMN_0024",
        "heavy": "ID_CMD_CMN_0025"
    }

    attacks = {
        "punch": ("ID_CMD_CMN_0006", "ID_CMD_CMN_0042"),
        "kick": ("ID_CMD_CMN_0007", "ID_CMD_CMN_0043")
    }

    s = stances[stance]
    m = strengths[strength]
    name, input_id = attacks[attack]

    return {
        "template": template,
        "strings": [
            s, m, name, "",
            s, m, input_id, ""
        ],
        "action_ids": action_ids
    }


RYX_CUSTOM_MOVES.update({

    "st_mp": normal_move(
        (14, 3), "standing", "medium",
        "punch", [2, 3, 14, 15]
    ),

    "st_lk": normal_move(
        (23, 5), "standing", "light",
        "kick", [6, 7, 18, 19]
    ),

    "st_hk": normal_move(
        (23, 5), "standing", "heavy",
        "kick", [10, 11, 22, 23]
    ),

    "j_lp": normal_move(
        (17, 1), "jumping", "light",
        "punch", [36, 37, 48, 49]
    ),

    "j_hp": normal_move(
        (17, 1), "jumping", "heavy",
        "punch", [40, 41, 52, 53]
    ),

    "j_lk": normal_move(
        (14, 1), "jumping", "light",
        "kick", [42, 43, 54, 55]
    ),

})

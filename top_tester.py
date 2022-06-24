from poss_loader import PossLoader
from valid_sub_attr_grader import ItemGrader, ItemRuleLoader
from single_pos_single_draw_layer import PaLayer
from single_pos_multi_draw_layer import PsLayer
from multi_pos_multi_draw_41 import PLayer41

import sys
import json



def double_write(fp, content):
    print(content)
    fp.write(content)
    fp.write("\n")


if __name__ == "__main__":
    poss_loader = PossLoader("drop_possibility_unicode.csv", "item_possibility_unicode.csv")
    char_rule_loader = ItemRuleLoader("character_detail.txt")

    def handle_single_char(character, fp):
        grader_1 = ItemGrader(char_rule_loader.char_rule_map[character], char_rule_loader.char_hash_map[character])
        pa_layer_1 = PaLayer(poss_loader, grader_1)
        ps_layer_1 = PsLayer(poss_loader, pa_layer=pa_layer_1, MAX_T=20001)
        p_layer_1 = PLayer41(poss_loader, ps_layer_1, single_piece_Q=10, target_t_list=[35, 70, 140, 140*2, 140*3, 140*6, 140*12])

        double_write(fp, character)
        double_write(fp, json.dumps(p_layer_1.get_expectation(), indent=4, ensure_ascii=False))

    with open("result_out.txt", "w", encoding="utf8") as fout:

        if sys.argv[1] == "all":
            # multi mode
            for character in char_rule_loader.char_rule_map.keys():
                handle_single_char(character, fout)
        else:
            # single mode
            if sys.argv[1] in char_rule_loader.char_rule_map:
                handle_single_char(sys.argv[1], fout)
            else:
                print("角色{}尚未在character_detail.txt中定义！")
    


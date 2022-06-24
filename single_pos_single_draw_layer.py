import json
import os
from poss_loader import PossLoader
from valid_sub_attr_grader import ItemGrader, ItemRuleLoader
from utils import random_choice_one_among_poss_map

class PaLayer:
    # 用于计算一个指定组件单次抽取的有效词次条数量的概率分布

    def __init__(self, poss_loader:PossLoader, grader:ItemGrader, allow_cache=True):
        self.poss_loader = poss_loader
        self.grader = grader

        # P_a(A, m)
        self.item_sub_num = {}

        cache_path = self.cache_path()
        if allow_cache and os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf8") as fin:
                self.item_sub_num = json.loads(fin.read())
            print("已加载Pa缓存")
        else:
            self.init_poss_distribute()

        # print(json.dumps(self.item_sub_num, indent=4, ensure_ascii=False))

    def cache_path(self):
        return "pa_layer_cache_{}.cache".format(self.grader.rule_hash)


    def init_poss_distribute(self, sample_time=100000):
        self.item_sub_num = {}
        for item_pos in self.poss_loader.item_pos_list:
            self.item_sub_num[item_pos] = {}

            for i in range(19):
                self.item_sub_num[item_pos][str(i*0.5)] = 0

            for main_attr in self.poss_loader.main_attr_list:
                current_main_attr_poss = self.poss_loader.main_attr_poss_map[item_pos][main_attr]
                if (item_pos, main_attr) not in self.grader.main_rule_map:
                    self.item_sub_num[item_pos]["0.0"] += current_main_attr_poss
                    continue

                temp_item_sub_num = {}
                for i in range(19):
                    temp_item_sub_num[str(i*0.5)] = 0
                
                for i in range(sample_time):
                    new_item = self.poss_loader.random_draw(item_pos=item_pos, main_attr=main_attr)
                    score = self.grader.grade(new_item)
                    base_score = score // 0.5 * 0.5
                    temp_item_sub_num[str(base_score)] += 1
                
                for i in range(19):
                    temp_item_sub_num[str(i*0.5)] /= sample_time
                
                # merge to total
                for i in range(19):
                    self.item_sub_num[item_pos][str(i*0.5)] += temp_item_sub_num[str(i*0.5)] * current_main_attr_poss
        
        with open(self.cache_path(), "w", encoding="utf8") as fout:
            fout.write(json.dumps(self.item_sub_num))

        print("所有部位单个圣遗物副次条期望预计算完成")

    
    def draw(self, item_pos):
        return random_choice_one_among_poss_map(self.item_sub_num[item_pos])


if __name__ == "__main__":
    poss_loader = PossLoader("drop_possibility_unicode.csv", "item_possibility_unicode.csv")
    char_rule_loader = ItemRuleLoader("character_detail.txt")
    grader = ItemGrader(char_rule_loader.char_rule_map["雷电将军"], char_rule_loader.char_hash_map["雷电将军"])
    pa_layer = PaLayer(poss_loader, grader)
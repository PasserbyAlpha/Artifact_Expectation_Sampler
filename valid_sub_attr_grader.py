
import json
import hashlib

class ItemDetail:

    def __init__(self, item_pos, main_attr, sub_attr_map, base_sub_attr_num):
        self.item_pos = item_pos
        self.main_attr = main_attr
        self.sub_attr_map = sub_attr_map
        self.base_sub_attr_num = base_sub_attr_num
        
    def check_print(self):
        print("{}{}副词条情况：".format(self.main_attr, self.item_pos))
        print(json.dumps(self.sub_attr_map, indent=4, ensure_ascii=False))


class ItemRuleLoader:
    def __init__(self, rule_file):

        self.char_rule_map = {}
        self.char_hash_map = {}

        with open(rule_file, "r", encoding="utf8") as fin:
            while True:
                char_name = fin.readline().strip()
                if char_name == "":
                    break


                main_attr_line = fin.readline().strip()
                sub_attr_line = fin.readline().strip()
                
                self.char_hash_map[char_name] = hashlib.md5((main_attr_line+sub_attr_line).encode()).hexdigest()

                main_attr_strs = main_attr_line.split(",")
                sub_attr_strs = sub_attr_line.split(",")

                main_attr_rule_map = {}
                for single_main_attr_str in main_attr_strs:
                    item_pos = single_main_attr_str[-1]
                    main_attr = single_main_attr_str[:-1]
                    main_attr_rule_map[(item_pos, main_attr)] = 1
                sub_attr_rule_map = {}
                for single_sub_attr_str in sub_attr_strs:
                    sub_div = single_sub_attr_str.split("=")
                    sub_name = sub_div[0]
                    sub_val = 1.0
                    if len(sub_div) > 1:
                        sub_val = float(sub_div[1])
                    sub_attr_rule_map[sub_name] = sub_val

                self.char_rule_map[char_name] = (main_attr_rule_map, sub_attr_rule_map)


class ItemGrader:

    def __init__(self, char_rule_map, rule_hash, poss_loader):
        # 假定评分字典是副次条=>评分的映射
        self.main_rule_map, self.sub_rule_map = char_rule_map
        self.rule_hash = rule_hash
        self.poss_loader = poss_loader


    def should_see_full_sub_attr(self, new_item):
        # 在什么情况下选择+4看词条
        # 默认是全部情况
        return True


    def should_gamble(self, new_item:ItemDetail):
        # 在什么情况下选择强化满看结果
        # 默认是要求大词条总计1.99分以上有效词条（即0.5词条此时暂时算0分）
        # 可以通过设置词条权重为0.99在不影响词条评分的情况下影响赌词条逻辑
        # （例如攻双暴充，要求最起码单暴+攻/充，或者攻充精双爆要有单暴或者攻充精全齐）
        # (特别的，为了解决有效词条太少的角色没有足够的词条，如果副词条已经出现了主词条以外所有有效词条则也要+20)

        # 主副词条情况特判
        max_sub_type_score = 0
        for sub_attr_name, sub_attr_weight in self.sub_rule_map.items():
            if sub_attr_weight > 0.75 and self.poss_loader.sub_attr_poss_map[new_item.main_attr][sub_attr_name] > 0:
                max_sub_type_score += sub_attr_weight

        valid_sub_attr_base_num = 0
        for sub_attr_name, sub_attr_num in new_item.sub_attr_map.items():
            if self.sub_rule_map.get(sub_attr_name, 0) > 0.5:
                valid_sub_attr_base_num += self.sub_rule_map.get(sub_attr_name, 0)
        return valid_sub_attr_base_num >= min(1.99, max_sub_type_score)

    def grade(self, new_item):
        # 检查主词条
        if (new_item.item_pos, new_item.main_attr) not in self.main_rule_map:
            return 0
        # 检查副次条强化条件
        single_sub_attr_limit = [10, 10, 10, 10]

        if new_item.base_sub_attr_num == 3 and (not self.should_see_full_sub_attr(new_item)):
            single_sub_attr_limit = [1, 1, 1, 0]
        elif not self.should_gamble(new_item):
            single_sub_attr_limit = [1, 1, 1, 1]

        # 检查副次条
        score = 0
        counter = 0
        for sub_attr_name, sub_attr_num in new_item.sub_attr_map.items():
            if sub_attr_name in self.sub_rule_map:
                score += min(sub_attr_num, single_sub_attr_limit[counter]) * self.sub_rule_map[sub_attr_name]
            counter += 1
        
        return round(score/0.5)*0.5

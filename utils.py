import random

def random_choice_one_among_poss_map(poss_map):
    # 假定概率字典为 key:possibility
    random_num = random.random()
    last_key = None
    for key, key_poss in poss_map.items():
        random_num -= key_poss
        last_key = key
        if random_num <=0:
            return key
    return last_key


def random_choice_multi_among_poss_map(poss_map, choose_num):
    # 假定概率字典为 key:possibility
    choose_set = set()
    remove_possible = 0
    compensate_arg = 1 / (1-remove_possible)

    for choose_idx in range(choose_num):

        random_num = random.random()
        last_key = None
        for key, key_poss in poss_map.items():
            if key in choose_set:
                continue
            random_num -= key_poss * compensate_arg
            last_key = key
            if random_num <=0:
                break

        choose_set.add(last_key)
        remove_possible += poss_map[last_key]
        compensate_arg = 1 / (1-remove_possible)
    
    return choose_set
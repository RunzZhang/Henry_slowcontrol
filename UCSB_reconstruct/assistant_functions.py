import copy


def dir_to_list(dic):
    list = []
    for key0 in dic:
        for key1 in dic[key0]:
            list.append(dic[key0][key1])
    list_sort = sorted(list)
    print(list_sort)
    return list_sort

def list_to_dir(list,dict):
    # this will miss the last line!!!!
    for key0 in dict:
        for key1 in dict[key0]:
            dict[key0][key1] = list[len(dict[key0])*key0+key1]
    print(dict)

dict = {
            0: {0: 3321, 1: 6225, 2: 2123, 3: 2124, 4: 2125},
            1: {0: 1202, 1: 2203, 2: 6202, 3: 6206, 4: 6210},
            2: {0: 6223, 1: 6224, 2: 6219, 3: 6221, 4: 6214}}
dict_1 = copy.deepcopy(dict)
list_output = dir_to_list(dict)
list_to_dir(list_output, dict_1)
            
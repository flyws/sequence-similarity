class S2MP(object):
    """A similarity measure realization from S2MP thesis"""

    def __init__(self):
        super(S2MP, self).__init__()

    def fit(self, sequence_a, sequence_b):
        self.sequence_a = sequence_a
        self.sequence_b = sequence_b
        self.mapOrder()

    def calculate_weight(self, list_a, list_b):
        intersec = list(set(list_a).intersection(set(list_b)))
        if len(list_a) + len(list_b) == 0:
            return 1
        weight = len(intersec) / (len(list_a) + len(list_b)) * 2
        return weight

    def mapOrder(self):
		# two problems: utility value == 0 | no better alternative assigned as -1
		# needs to be solved somehow. Drop zero values, and tell the module to
		# skip those who have no better alternatives.
        mapOrder = []
        for index_a, item_a in enumerate(self.sequence_a):
            weight_list = list(map(lambda x: self.calculate_weight(item_a, x), self.sequence_b))
            mapOrder.append([index_a, weight_list])
        # by default, the i.index(max) will return the max with the lower time rank
        mapped_set = [i[1].index(max(i[1])) for i in mapOrder]
        # nested loop with different starting points to solve conflict
        for i in range(0, len(mapped_set)):
            mo_i = mapped_set[i]
            for j in range(i + 1, len(mapped_set)):
                if mo_i == mapped_set[j]:
                    itemset = self.solve_conflict(i, j, mapped_set, mapOrder)
                    # decide if i or j should be kept in the sequence_a when there's no alternative
                    if itemset == None:
                        sc1 = mapOrder[i][1][self.conflict_index[0][1]]
                        sc2 = mapOrder[j][1][self.conflict_index[0][1]]
                        # changed from ">" to ">=" to deal with double mapped index at the end
                        if sc1 >= sc2:
                            mapped_set[j] = -1
                        else:
                            mapped_set[i] = -1
                        break
                    for k in itemset:
                        mapped_set[k[0]] = k[1]
        # deal with zero utility problem (according to the essay, no need to include 0)
        pop_index = list()
        for index, value in enumerate(mapped_set):
        	if (mapOrder[index][1][value] == 0) and (value != -1):
        		pop_index.append(index)
        if len(pop_index) != 0:
        	mapped_set = [x for i, x in enumerate(mapped_set) if i not in set(pop_index)]
        # deal with double/trippled or even "monster kill" mapped index if they are not near to each other
        another_pop_list = [index for index, value in enumerate(mapped_set) if mapped_set.count(value) > 1]
        for i in another_pop_list[1:]:
        	mapped_set.pop(i)
        self.mapOrderList = mapped_set
        return mapped_set

    def solve_conflict(self, k, j, mapped_set, mapOrder):
        conflict_index = [[index, item] for index, item in enumerate(mapped_set)]
        # get only the conflict between the requested two indexes
        conflict_index = [conflict_index[k], conflict_index[j]]
        possible_combination = []
        self.mapped_set = mapped_set
        self.conflict_index = conflict_index
        # get possible combination as indexes' list
        for i in conflict_index:
            # set sequence a as the benchmark, and find the next best in sequence b
            nextMaxBefore = self.nextMaxBefore(mapOrder[i[1]][1], i[1])
            nextMaxAfter = self.nextMaxAfter(mapOrder[i[1]][1], i[1])
            # exclude mapped index in the past
            if (nextMaxBefore != None) and (nextMaxBefore not in self.mapped_set[:k]):
                possible_combination.append([i[0], nextMaxBefore])
            if (nextMaxAfter != None) and (nextMaxAfter not in self.mapped_set[:k]):
                possible_combination.append([i[0], nextMaxAfter])
        reordered_list = []
        
        if not possible_combination:
            return None

        for i in conflict_index:
            for j in possible_combination:
                # I would only need those who comply with orders
                if (i[0] != j[0]):
                    reordered_list.append([i, j])
        itemset = reordered_list[self.localSim(reordered_list)]
        return itemset

    def localSim(self, reordered_list):
        '''return the index in reordered_list with the highest localSim value'''
        localSim = 0
        localSimValue = 0
        # loop through all four possible combinations
        for index, item in enumerate(reordered_list):
            list_temp = item
            # get mapped values from sequence a and b
            values = list(map(lambda x: [self.sequence_a[x[0]], self.sequence_b[x[1]]], list_temp))
            # deal with conditions that two lists are empty list
            if values[0] == values[1]:
                if (list_temp[0][0] < list_temp[1][0]) and (list_temp[0][1] < list_temp[1][1]):
                    return index
                else:
                    pass
            # mappings that comply with the order
            elif (list_temp[0][0] - list_temp[1][0]) * (list_temp[0][1] - list_temp[1][1]) > 0:
            	benchmark = (self.calculate_weight(values[0][0], values[0][1]) + \
            					self.calculate_weight(values[1][0], values[1][1])) * 1/2
            	if localSimValue < benchmark:
                    localSim = index
                    localSimValue = benchmark
            # cross mapping
            elif (list_temp[0][0] - list_temp[1][0]) * (list_temp[0][1] - list_temp[1][1]) < 0:
            	benchmark = (self.calculate_weight(values[0][0], values[0][1]) + \
            					self.calculate_weight(values[1][0], values[1][1])) * 1/4
            	if localSimValue < benchmark:
                    localSim = index
                    localSimValue = benchmark
            # for DEBUG usages
            # print(index, benchmark)
        return localSim

    def nextMaxBefore(self, sequence, position):
        # if this is already the beginning
        if not sequence[0:position]:
            return None
        max_index = sequence[0:position].index(max(sequence[0:position]))
        if sequence[max_index] == 0:
            return None
        return max_index

    def nextMaxAfter(self, sequence, position):
        # if this is the ending
        if not sequence[position + 1:]:
            return None
        max_index = sequence[position + 1:].index(max(sequence[position + 1:]))
        # need an offset to get original position
        max_index = position + 1 + max_index
        if sequence[max_index] == 0:
            return None
        return max_index

    def AveWeightScore(self):
        # natural_order = range(0, len(self.sequence_a))
        # sum_value = list(map(lambda x, y: self.calculate_weight(self.sequence_a[x], self.sequence_b[y]),
        #                                                       natural_order, self.mapOrderList))
        # reritten with -1 method
        sum_value = 0
        count = 0
        for i in range(0, len(self.sequence_a)):
        	# add the catch system to deal with those that has dropped useless items
        	try:
	            if self.mapOrderList[i] > -1:
	                sum_value += self.calculate_weight(self.sequence_a[i], self.sequence_b[self.mapOrderList[i]])
	                count += 1
	        except IndexError:
	        	pass
        avg_value = sum_value / count
        return avg_value

    def OrderedItemSets(self):
        # get ordered list among the list, and the number of ordered itemsets
        # starting to get rid of -1 values from here
        self.mapOrderList = [i for i in self.mapOrderList if i != -1]
        OrderedItemSets = []
        increasing_bool = [(self.mapOrderList[k + 1] - self.mapOrderList[k]) > 0
                           for k in range(len(self.mapOrderList) - 1)]
        temp_list = []
        for index, item in enumerate(increasing_bool):
            if item == True:
                temp_list.append(self.mapOrderList[index])
                temp_list.append(self.mapOrderList[index + 1])
            elif len(increasing_bool) == 1:
                temp_list.append(self.mapOrderList[index])
            else:
                pass
        if len(increasing_bool) == 0:
            temp_list = [self.mapOrderList[0]]
        # keep the order when changing list to set
        OrderedItemSets.append(list(sorted(set(temp_list), key=temp_list.index)))
        self.OrderedItemList = OrderedItemSets
        return OrderedItemSets

    def orderScore(self):
        self.OrderedItemSets()
        # loop through separate maximum increasing subsequences
        temp_list = []
        for i, item in enumerate(self.OrderedItemList):
            temp_list.append(self.totalOrder(i) * (1 - self.positionOrder(i)))
        return max(temp_list)

    def totalOrder(self, index):
        nbOrderedItemSets = len(self.OrderedItemList[index])
        totalOrder = nbOrderedItemSets / (len(self.sequence_a) + len(self.sequence_b)) * 2
        return totalOrder

    def positionOrder(self, index):
        aveNbItemSets = (len(self.sequence_a) + len(self.sequence_b)) / 2
        temp_list = self.OrderedItemList[index]
        sum_values = []
        for i in range(1, len(temp_list)):
            sum_values.append(abs((temp_list[i] - temp_list[i - 1]) -
                                  (self.mapOrderList.index(temp_list[i]) - self.mapOrderList.index(
                                      temp_list[i - 1]))))
        positionOrder = sum(sum_values) / aveNbItemSets
        return positionOrder

    def SimDegree(self, a=0):
        if a == 0:
            return self.AveWeightScore() * self.orderScore()
        elif a > 0 and a <= 1:
            return a * self.AveWeightScore() + (1 - a) * self.orderScore()
        else:
            raise ValueError("a must be between 0 and 1")


if __name__ == '__main__':
    a = S2MP()
    # M1 is the standard sequence
    M1 = [['A', 'B', 'C'], ['B'], ['C']]
    M2 = [['A', 'C'], ['B'], ['C', 'D']]
    a.fit(M1, M2)
    print(a.AveWeightScore(), a.orderScore())
    print(a.SimDegree(0.1))
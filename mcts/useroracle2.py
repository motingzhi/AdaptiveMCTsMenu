import random
import math
from enum import Enum
from copy import deepcopy
import utility

class UserStrategy(Enum):
    AVERAGE = 0
    SERIAL = 1
    FORAGE = 2
    RECALL = 3

class UserOracle(): 
    separator = "----"
    def __init__(self,maxdepth, associations):
        self.maxdepth = maxdepth
        self.alpha = 2.0 # Inspection cost (in seconds) under caution.
        self.groupreadingcost = 0.5 # Foraging model's cost for switching a menu group
        self.vicinity = 1 # +/- range of the vicinity (nearby) items
        self.surprisecost = 0.2 # 
        self.point_const = 0.4
        self.associations = associations
    # Reading cost: modulated by experience
    def read(self,item, menu, novice = False):
        if item == self.separator:
            return 0.0
        if novice: return self.alpha
        # simple_menu = list(filter(("----").__ne__, menu)) # menu without separators
        if item not in self.activations.keys():
            return self.alpha
        item_activations = self.activations[item] 
        total_activation = sum(item_activations.values())
   
        return self.alpha/(1+total_activation)

    # Linear search time: Word reading time modulated by experience
    def serialsearch2(self, target, currentmenu, previousmenu = None, novice = False):
        if previousmenu == None: previousmenu = currentmenu
        currentmenu = list(filter(("----").__ne__, currentmenu)) # menu without separators
        previousmenu = list(filter(("----").__ne__, previousmenu)) # menu without separators
        t = 0.0
        if target == self.separator: return 0.0
        targetlocation = currentmenu.index(target)
        expectedlocation = previousmenu.index(target)
        if (targetlocation <= expectedlocation):
            # Target appears at, or before, previously seen location. Read serially till found
            for i in range (0, targetlocation+1):
                t += self.read(currentmenu[i], currentmenu, novice)
        else:
            # Target position adapted => moved to a position after expected.
            # First, read at regular speed till expected position
            for i in range (0, expectedlocation + 1):
                t += self.read(currentmenu[i], currentmenu, novice)
            # Target not found yet. 
            t += self.surprisecost # Surprise cost added on not finding target
            for i in range (expectedlocation+1, targetlocation+1):
                t += self.read(currentmenu[i],currentmenu, novice = True) # Read as novice until new target position
        return round(t,5)

    def serialsearch(self,target, currentmenu, previousmenu = None, novice = False):
        if previousmenu == None: previousmenu = currentmenu

        # currentmenu = list(filter(("----").__ne__, currentmenu)) # menu without separators
        # previousmenu = list(filter(("----").__ne__, previousmenu)) # menu without separators

        # n1= number of split items before adaptation
        # n2 = number of split items after adapatation

        n1 = 0
        n2 = 0
        for n in range(0,5):
            if currentmenu[n] != "-":
                n2 = n2+1
            if previousmenu[n] != "-":
                n1 = n1+1
        # print("nn",n1,n2)


        t = 0.0
        if target == self.separator: return 0.0
        if target == "-": return 0.0
        ###location in the menu ( not split menu?)
        # targetlocation = currentmenu.index(target)
        # expectedlocation = previousmenu.index(target)
        # for n  in range(0, 5):
        #     if target == previousmenu[n]:
        #         expectedlocation = n
        #
        # print("ep",expectedlocation)

        expectedinsplit = 0
        targetinsplit = 0
        for m in range(0,5):
            if target == previousmenu[m]:###########expect location in the split items
                expectedlocation = m
                expectedinsplit = 1

                break
            else:
                expectedinsplit = 2
            if target == currentmenu[m]:# and expectedinsplit == 1:###actual location is in the split items
                targetinsplit = 1
                targetinsplit_location = m
                break
            else:
                targetinsplit = 2#false
        if targetinsplit ==2 and expectedinsplit ==1 :
            for n in range(11, 16):
                # print("目前1",target,currentmenu[n])
                if target == currentmenu[n]:
                    targetlocation = n  ######此处不用程序内运行的current menu,而是用自己給的那个
                    t += self.surprisecost
                    # print("目前2", currentmenu,t)
                ####reading time for show the
                    for x in range(0, 5):


                        if currentmenu[x] != "-":
                            t += self.read(currentmenu[x], currentmenu, novice)
                            # print("目前3", x)
                            # print("4", currentmenu[x])
                            # print("5", t)
                            # print(self.read(currentmenu[x], currentmenu, novice))

                    for i in range(11, targetlocation + 1):
                        t += self.read(currentmenu[i], currentmenu, novice)
                        # print("6",self.read(currentmenu[i], currentmenu, novice))
                        # print("7",t)

        if  targetinsplit ==1 and expectedinsplit ==1 :
            targetlocation = targetinsplit_location
            if (targetlocation <= expectedlocation):
                for i in range(0, targetlocation + 1):
                    if currentmenu[i] != "-":
                        t += self.read(currentmenu[i], currentmenu, novice)
                    # t += self.read(currentmenu[i], currentmenu, novice)
            else:
                # Target position adapted => moved to a position after expected.
                # First, read at regular speed till expected position
                for i in range(0, expectedlocation + 1):
                    if currentmenu[i] != "-":
                        t += self.read(currentmenu[i], currentmenu, novice)
                    # t += self.read(currentmenu[i], currentmenu, novice)
                # Target not found yet.
                t += self.surprisecost  # Surprise cost added on not finding target
                for i in range(expectedlocation + 1, targetlocation + 1):
                    if currentmenu[i] != "-":
                        t += self.read(currentmenu[i], currentmenu, novice)
                        #print("有吗")
                    # t += self.read(currentmenu[i], currentmenu,
                    #                novice=True)  # Read as novice until new target position


        # if expectedinsplit== 2:###expected item is not in the previous menu
        #     for a in range(0,5):
        #         if
        if expectedinsplit== 2 and targetinsplit ==1 :
            targetlocation= targetinsplit_location
            for i in range(0, targetlocation + 1):
                if currentmenu[i] != "-":
                    t += self.read(currentmenu[i], currentmenu, novice)
                # t += self.read(currentmenu[i], currentmenu, novice)

        if expectedinsplit ==2 and targetinsplit ==2:
            for d in range(11, 16):
                if target == currentmenu[d]:
                    targetlocation = d
                    for i in range(11, targetlocation + 1):
                         t += self.read(currentmenu[i], currentmenu, novice)







        # if (targetlocation <= expectedlocation):
        #     # Target appears at, or before, previously seen location. Read serially till found
        #     for i in range (0, targetlocation+1):
        #         t += self.read(currentmenu[i], currentmenu, novice)
        # else:
        #     # Target position adapted => moved to a position after expected.
        #     # First, read at regular speed till expected position
        #     for i in range (0, expectedlocation + 1):
        #         t += self.read(currentmenu[i], currentmenu, novice)
        #     # Target not found yet.
        #     t += self.surprisecost # Surprise cost added on not finding target
        #     for i in range (expectedlocation+1, targetlocation+1):
        #         t += self.read(currentmenu[i],currentmenu, novice = True) # Read as novice until new target position
        return round(t,5)

    # Foraging time. Model is similar to Freire et al. 2019 PMC
    # def forage(self, target, currentmenu, previousmenu = None):
    #     if previousmenu == None: previousmenu = currentmenu
    #     t = 0.0
    #     if target == self.separator: return 0.0
    #     header_indexes = utility.get_header_indexes(currentmenu)
    #     # if (len(header_indexes) == 1): return self.serialsearch(target,currentmenu,previousmenu)
    #     # Found all group header indices. Now we start reading them, to compute foraging time
    #     for header_index in header_indexes: # Iterate through all header indices
    #         t += self.read(currentmenu[header_index], currentmenu) # Read the header
    #         if currentmenu[header_index] == target: return round(t,5) # Header is the target item. Finish.
    #         if target in self.associations[currentmenu[header_index]]: # Target associated to this group header
    #             # read within group
    #             for i in range(header_index+1,len(currentmenu)):
    #                 if currentmenu[i] == self.separator: # End reading when group ends
    #                     break
    #                 t += self.read(currentmenu[i], currentmenu)
    #                 if currentmenu[i] == target: return round(t,5) # Found. Finish here.
    #                 elif currentmenu[i] not in self.associations[currentmenu[header_index]]: t += self.surprisecost # Unexpected item found in group
    #             t += self.groupreadingcost # Not found in the group. Add confusion penalty, move to next group
    #     # Target still not found after foraging
    #     t += self.serialsearch(target, currentmenu, None, novice = True)
    #     return round(t,5)

    # Recall model: recall probability is modulated by experience
    # Inspired by Bailly et al. CHI 2014
    # def recall(self, target, currentmenu, previousmenu = None):
    #     if previousmenu == None: previousmenu = currentmenu
    #     if target == self.separator: return 0.0
    #     t = 0.0
    #     if target not in self.activations: # Item not seen before. Revert to serial search
    #         return (self.serialsearch(target, currentmenu, previousmenu))
    #     max_activation = max(self.activations[target].values()) # Total activation for the target item
    #     if max_activation < 0.5:
    #         # No activation point above threshold. Revert to serial search
    #         return (self.surprisecost + self.serialsearch(target, currentmenu, previousmenu))
    #     else:
    #         simple_menu = list(filter(("----").__ne__, currentmenu)) # menu without separators
    #         # Attempt recall search in descending order of activation level
    #         pointing_time = self.point_const * math.log(2*(simple_menu.index(target) + 1),2) # Basic Fitts' model
    #         t += pointing_time
    #         for position,activation in sorted(self.activations[target].items(), key=lambda x: x[1], reverse=True):
    #             # Iterate over activated locations. User searches in positions with activation > threshold
    #             if activation >= 0.5:
    #                 t += self.read(simple_menu[position],currentmenu) # Read item at activated position
    #                 if simple_menu[position] == target:
    #                     return round(t,5) # Target found. Finish here.
    #                 # Local search around the activated position.
    #                 distance = abs(simple_menu.index(target) - position)
    #                 if distance <= self.vicinity:
    #                     # Target is in vicinity of this position. Finish after reading around here.
    #                     t += (2*distance - 0.5)*self.alpha
    #                     return round(t,5)
    #                 else:
    #                     # Failed local search after inspecting all vicinity items
    #                     t += 2*self.vicinity*self.alpha
    #                 t += self.surprisecost # Add cost for searching another activation point
    #
    #         # Target still not found. Fall-back to slow cautious serial search
    #         t += self.serialsearch(target,currentmenu, previousmenu = None, novice = True)
    #     return round(t,5)
    
    #Average search time (weighted by itemfrequency) for each model
    def get_average_times(self, frequency, currentmenu, previousmenu = None):
        if previousmenu == None: previousmenu = currentmenu
        serial_time = 0.0
        # forage_time = 0.0
        # recall_time = 0.0
        for i in range (0, len(currentmenu)):
            target = currentmenu[i]
            if target == self.separator: continue
            #print("user2",frequency)
            serial_time += frequency[target] * self.serialsearch(target, currentmenu, previousmenu)
            # forage_time += frequency[target] * self.forage(target, currentmenu, previousmenu)
            # recall_time += frequency[target] * self.recall(target, currentmenu, previousmenu)

        # return serial_time,forage_time,recall_time

        return serial_time

    def get_individual_rewards(self,state):

        currentmenu = state.menu_state.simplified_menu()#[0:5]#state是plan_simple 里的 root_state；plan_simple 里的 root_state = State（state.py里的）menu_state,user_state, exposed=True)
        #print("currentmenu",currentmenu)
        self.activations = state.user_state.activations
        frequency = state.user_state.freqdist

        previousmenu = None
        if state.previous_seen_state is not None:
            previousmenu = state.previous_seen_state.menu_state.simplified_menu()
 
        # new_serial_time, new_forage_time, new_recall_time = self.get_average_times(frequency, currentmenu, previousmenu)
        new_serial_time = self.get_average_times(frequency, currentmenu, previousmenu)
        if not previousmenu or not state.exposed: #  root state or not exposed
            return [0.0,0.0,0.0], [new_serial_time]

        previous_serial_time= self.get_average_times(frequency, previousmenu)

        reward_serial = previous_serial_time - new_serial_time
        # reward_forage = previous_forage_time - new_forage_time
        # reward_recall = previous_recall_time - new_recall_time
        return [reward_serial  ], [new_serial_time ]
        #return [reward_serial, reward_forage, reward_recall], [new_serial_time, new_forage_time, new_recall_time]
        
    def is_terminal (self, state):       
        if state.depth >= self.maxdepth:
            return True
        return False

    def __str__(self):
        return (self.maxdepth)
    
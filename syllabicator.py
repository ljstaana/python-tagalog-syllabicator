import json
import re

class Syllabicator: 

    def __init__(self, config): 
        self.verbose = config["verbose"]    

        # consonant clusters         
        self.clusters = self.treefy([
            "bl", "br", 
            "dr", "dy", 
            "gr", "kr", 
            "kr", "ky",
            "pl", "pr", 
            "sw",
            "tr", "ts"
        ])

        # vowels 
        self.vowels =  self.treefy([
            "a", "e", "i", "o", "u"
        ]) 

        # processing variables 
        self.buffers = "" 
        self.syllables = [] 
        self.word = "" 

    # helper function for printing procedures
    def print_verbose(self, text=""): 
        if self.verbose: 
            print(text)
        else:
            return None 

    # hashmaps a consonant cluster for optimization 
    def treefy(self, array): 
        hash = {} 
        for val in array: 
            # lookup 
            lookup = hash 
            for i in range(len(val)): 
                letter = val[i]
                if i > len(val) - 1: 
                    break 
                role = {} 
                if i == len(val) - 1: 
                    role = True 
                if letter not in lookup: 
                    lookup[letter] = role 
                lookup = lookup[letter]
            lookup = hash 
        return hash 
    
    # returns the first consonant cluster 
    # that is matched by a word with priority on longer 
    # clusters
    def tree_match(self, cluster, index): 
        result = "" 
        lookup = cluster 
        # get the piece of the word from index to the last letter 
        string = self.word[index:] 
        for i in range(len(string)): 
            letter = string[i] 
            # look for the current letter in the clusters 
            if letter in lookup:
                lookup_t = lookup[letter] 
            else: 
                return False
            if type(lookup_t) == type({}): 
                # if found, then change lookup and add letter to buffer
                lookup = lookup_t 
                result += letter 
            elif lookup_t == True: 
                # return the result 
                result += letter 
                break 
            else: 
                # if not found, then quit and return not a cluster 
                return False
        return result 

    # ----------- IMPLEMENTATION FUNCTIONS ----------------- #

    def print_state(self): 
        print("STATE ======================")
        print("Buffers: ", self.buffers)
        print("Syllables: ", self.syllables)
        print("============================")

    def start(self): 
        print("Init Word: " + self.word)
        next_index = 0
        # check if a cluster 
        cluster = self.tree_match(self.clusters, next_index)
        # if a cluster, then add the current cluster to the current buffer
        if cluster != False: 
            self.print_verbose("Cluster start")
            self.buffers += cluster 
            print("Buffers: ", self.buffers)
            next_index = len(cluster)
        else: 
            print("Not a cluster...")
            next_index = self.vowels_and_consonants(next_index)
        # start operation on the second letter
        self.op_flow(next_index) 
        # if last syllable is a sole consonant on > 2 syllables
        # merge it with the last syllable 
        if self.is_consonant(self.syllables[-1]) and \
           len(self.syllables) > 1 and \
           len(self.syllables[-1]) == 1: 
           self.syllables[-2] = self.syllables[-2] + self.syllables[-1] 
           self.syllables.pop() 

    # flow mode operations
    def op_flow(self, index): 
        self.print_verbose("After-init ...")
        self.print_verbose("@ op_flow()")
        self.print_state()
        next_index = index 
        while next_index < len(self.word): 
            next_index = self.vowels_and_consonants(next_index)
            print("Next index: ", next_index)
        self.integrate_buffer() 
    

    def are_letters_next(self, index, letters): 
        endd = index + len(letters) 
        print("Are letters next " + str(letters))
        if endd < len(self.word): 
            print("Word: " + self.word[index:], "Letters: " + letters)
            if self.word[index:] == letters: 
                return True
            else: 
                return False
        else:
            return False 
    
    def validate_special_after_vowel(self, index, letters): 
        length = len(letters) 
        return self.is_vowel(self.word[index - 1]) and self.are_letters_next(index, letters) and \
               self.is_consonant(self.word[index + length]) 

    # rule 1: consonant vowels (general rules)
    def vowels_and_consonants(self, index):
        print("------------------------------------------------------------------------")
        print("vowels_and_consonants(" + str(index) + ")")
        goto_index = index 
        letter = self.word[index]
        if self.is_vowel(self.word[index]): 
            print("Is vowel..." + self.word[index])
            self.print_state()
            if self.buffers != "": 
                if self.is_vowel(self.buffers[-1]): 
                    self.integrate_buffer() 
                    print("Int. buffer...")
                    self.buffers = letter 
                else: 
                    self.buffers += letter 
            else: 
                self.buffers += letter 
            goto_index += 1
        else: 
            print("Is consonant..." + self.word[index])
            if index == len(self.word) - 1: 
                self.buffers += letter 
                self.print_state()
                return index + 1 
            
            # SPECIAL CASES
            if self.word[index] == "@": 
                if self.is_consonant(self.word[index + 1]):
                    self.buffers += "@"
                    return index + 1

            if self.validate_special_after_vowel(index, "sk"): 
                print("Special case sk")
                self.buffers += "sk"
                self.integrate_buffer() 
                self.buffers = "" 
                return index + 2 
            if self.validate_special_after_vowel(index, "ky"): 
                print("Special case ky")
                self.buffers += "ky"
                self.integrate_buffer() 
                self.buffers = "" 
                return index + 2 
            if self.validate_special_after_vowel(index, "st"):
                print("Special case st")
                self.buffers += "st"
                self.integrate_buffer() 
                self.buffers = "" 
                return index + 2 
            if self.validate_special_after_vowel(index, "nst"): 
                print("Special case nst")
                self.buffers += "nst" 
                self.integrate_buffer() 
                self.buffers = "" 
                return index + 3 
            if self.validate_special_after_vowel(index, "mp") and \
                self.word[index + 2] == "r": 
                print("Special case mpr")
                self.buffers += "mp"
                self.integrate_buffer() 
                self.buffers = "" 
                return index + 2 
            
            # MIDWORD CONSONANTS
            count = 0
            for i in range(4): 
                look_at = i + index
                print("Look at: " + str(look_at))
                if look_at < len(self.word): 
                    print("is_consonant(" + str(self.word[look_at]) + ") = " + str(self.is_consonant(self.word[look_at])))
                    if self.is_consonant(self.word[look_at]): 
                        print("Count increase...")
                        count += 1 
                    else: 
                        break 

            print("Count: ", count)

            # apply rules depending on count 
            form = self.word[index:index+count] 

           

            # if only one consonant, the letter is part of a new syllable 
            if count == 1 or index == 0: 
                self.integrate_buffer() 
                self.buffers = form[0]
            # if two consonants, the first letter belongs
            # to the first syllable while the second belongs to the
            # second syllable 
            elif count == 2: 
                self.buffers += form[0]
                self.integrate_buffer() 
                self.buffers = form[1]
            # if three consonants, two rules can happen 
            elif count == 3: 
                # if a first letter is m or n, check if the
                # two other consonants is a cluster, if yes, add the
                # first letter in the form and integrate the current buffer
                # and the form to a new syllable with the cluster
                if ((form[0] == "m" or form[0] == "n" or form[0 == "s"])) and \
                    self.tree_match(self.clusters, index + 1): 
                    self.buffers += form[0]
                    self.integrate_buffer() 
                    self.buffers = form[1] + form[2]
                else: 
                # else, apply standard rules that say
                # the first two consonants belong to the 
                # first syllable while the other two belongs
                # to another
                    self.buffers += form[0] + form[1]
                    self.integrate_buffer() 
                    self.buffers = form[2]
            # if there are four words, then the rules in the paper
            # sats that the first two words are in one syllable while
            # the two are in another 
            elif count == 4: 
                self.buffers += form[0] + form[1]
                self.integrate_buffer() 
                self.buffers = form[2] + form[3]
            
            goto_index = index + count

            self.print_state()

            print("Goto index: " + str(goto_index))

        return goto_index 
    
    # special rules for the last letter
    def last_special_rules(self, index):
        letter = self.word[index] 
        if (index == len(self.word) - 1 and self.is_consonant(letter)) :
            if self.is_vowel(self.word[index - 1]): 
                self.buffers += letter 
            else: 
                self.syllables[-1] = self.syllables[-1] + letter 
                self.buffers = "" 
            return index + 1 
    
    # one of the major differences between OP and UP version
    # is how they treat consonant clusters in the middle of the word
    # using this function, consonant clusters will prioritized first.
    # this is technically the "start" of the word if it were in OP like case 
    def cluster_first(self, index): 
        next_index = index 
        if self.is_consonant(index): 
            # check if a cluster 
            cluster = self.tree_match(self.clusters, next_index) 
            # if a cluster, then add the current cluster to the current buffer
            if cluster: 
                self.integrate_buffer() 
                self.buffers = cluster 
                next_index = len(cluster) + next_index 
        return next_index

    # integrates the current buffer to the syllables array 
    def integrate_buffer(self, last=False): 
        buffer = re.sub("@", "ng", self.buffers)
        if self.buffers.strip() != "": 
            self.syllables.append(buffer)
    
    # -------------- HELPER FUNCTIONS --------- #*

    def is_vowel(self, lt): 
        return lt in self.vowels

    def is_consonant(self, lt):
        return not self.is_vowel(lt)

    def syllabicate(self, word): 
        self.word = word 
        self.word = re.sub("ng", "@", self.word)
        self.start() 
        syllables = self.syllables 
        self.syllables = [] 
        self.buffers = "" 
        return syllables

syllabicator = Syllabicator({
    "verbose": True
})


print(syllabicator.syllabicate("kalungkutan"))
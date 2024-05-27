

import sys
import math
from .smoothing import smooth_grammar, smooth_length




def dist(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def decrease_coordinates(pattern, i, j):
    result = [(x - i, y - j) for x, y in pattern]
    return tuple(result)


class AlphabetLookup:

    def __init__(self, alphabet, ngram, min_length = 2, max_length = 50):
        firstRow = "`1234567890-="
        firstRowShift = "~!@#$%^&*()_+"
        secondRow = "qwertyuiop[]\\"
        secondRowShift = "QWERTYUIOP{}|"
        thirdRow = "asdfghjkl;'"
        thirdRowShift = "ASDFGHJKL:\""
        fourthRow = "zxcvbnm,./"
        fourthRowShift = "ZXCVBNM<>?"
        allowed_chars = firstRow + firstRowShift + secondRow + secondRowShift + thirdRow + thirdRowShift + fourthRow + fourthRowShift
        keyboard = [firstRow, secondRow, thirdRow, fourthRow]
        keyboardShift = [firstRowShift, secondRowShift, thirdRowShift, fourthRowShift]
        self.keyboardDictionary = {}

        for i in range(0, len(keyboard)):
            for j in range(0, len(keyboard[i])):
                if i >= 1:
                    point = (j + 1, i)
                else:
                    point = (j, i)
                self.keyboardDictionary[keyboard[i][j]] = point

        for i in range(0, len(keyboardShift)):
            for j in range(0, len(keyboardShift[i])):
                if i >= 1:
                    point = (j + 1, i)
                else:
                    point = (j, i)
                self.keyboardDictionary[keyboardShift[i][j]] = point
        self.keyboardDictionary = self.keyboardDictionary
        self.patternDictionary = {}
        
        ##--Save input options
        self.alphabet = alphabet
        self.ngram = ngram
        self.max_length = max_length
        self.min_length = min_length
        
        ##--Min length can't be less than ngram
        if self.min_length < ngram:
            self.min_length = ngram


        {
            '((0, 0), (0, 0))': {  # Начальный шаблон (IP)
                'ip_count': 5,  # Количество раз, когда шаблон встречается в начале пароля (IP)
                'ep_count': 3,  # Количество раз, когда шаблон встречается в конце пароля (EP)
                'cp_count': 100,  # Общее количество раз, когда шаблон встречается в паролях (CP)
                'next_letter': {  # Следующий шаблон для CP
                    '((0, 0), (-1, 1))': 5, # Представляет CP '((0, 0), (0, 0)) -> ((0, 0), (-1, 1))'
    #                                         с количеством раз, когда CP был увиден
                    '((0, 0), (1, 1))': 12,  # Представляет CP '((0, 0), (0, 0)) -> ((0, 0), (1, 1))'
                    ...,
            },
        },
        ...,
        }
        {
            '((0, 0), (0, 0))': {  # Начальные символы (IP)
                'ip_count': 5,  # Количество раз, когда они встречаются в начале пароля (IP)
                'ep_count': 3,  # Количество раз, когда они встречаются в конце пароля (EP)
                'cp_count': 100,  # Общее количество раз, когда они встречаются в паролях (CP)
                'next_letter': {  # Следующая буква для CP
                    '((0, 0), (-1, 1))': 5, # Представляет CP '((0, 0), (0, 0)) -> ((0, 0), (-1, 1))' с количеством раз, когда CP был увиден
                    '((0, 0), (1, 1))': 12,  # Представляет CP '((0, 0), (0, 0)) -> ((0, 0), (1, 1))'
                    ...,
            },
        },
        ...,
        }

        self.grammar = {}

        self.ip_counter = 0

        self.ep_counter = 0      

        self.ln_counter = 0       
            
        self.ln_lookup = [0] * max_length

        return

    def parse(self, password):

        pw_len = len(password)
        if pw_len < self.min_length or pw_len > self.max_length:
            return


        pattern_list = []
        password = password.strip()
        password_list_cur = []
        pointStart = self.keyboardDictionary[password[0]]
        currentStartX = pointStart[0]
        currentStartY = pointStart[1]
        password_list_cur += [pointStart]
        pos = 1
        curSumLen = 0
        for symb in password[1:]:
            pos += 1
            point = self.keyboardDictionary[symb]
            if dist(password_list_cur[-1], point) < 2:
                password_list_cur += [point]
            else:
                if len(password_list_cur) > 1:
                    basePattern = decrease_coordinates(password_list_cur, currentStartX, currentStartY)
                    curSumLen += len(basePattern)
                    pattern_list.append(basePattern)
                password_list_cur = []
                currentStartX = point[0]
                currentStartY = point[1]
                password_list_cur += [point]
        if len(password_list_cur) > 1:
            basePattern = decrease_coordinates(password_list_cur, currentStartX, currentStartY)
            curSumLen += len(basePattern)
            pattern_list.append(basePattern)


        if curSumLen == len(password):
            self.ln_lookup[pw_len - 1] += 1
            self.ln_counter += 1
            pattern_list_size = len(pattern_list)
            for i in range(0, pattern_list_size - self.ngram + 2):
                ##--Grab the ngram-1 section to key off of
                cur_start_ngram = pattern_list[i:i+self.ngram-1][0]


                if cur_start_ngram  not in self.grammar:
                    if cur_start_ngram in self.alphabet:
                        self.grammar[cur_start_ngram] = {
                            'ip_count':0,
                            'ep_count':0,
                            'cp_count':0,
                            'next_letter':{},
                            }
                    ##--Not in alphabet, skip and go on to the next one
                    else:
                        continue

                ##--Just declaring this pointer here to clean up the folloiwng code
                index = self.grammar[cur_start_ngram]

                ########
                ##--Handle if it is the IP
                ########
                if i == 0:
                    index['ip_count'] += 1
                    self.ip_counter += 1


                ########
                ##--Handle the CP info
                ########
                if i != pattern_list_size - (self.ngram -1):
                    end_pattern = pattern_list[i+self.ngram-1]
                    ##--Check if this character has been seen before
                    if end_pattern not in index['next_letter']:
                        if end_pattern in self.alphabet:
                            index['next_letter'][end_pattern] = 1
                            index['cp_count'] += 1
                    ##--Have seen this before
                    else:
                        index['next_letter'][end_pattern] += 1
                        index['cp_count'] += 1

                #######
                ##--Handle the EP info
                #######
                else:
                    index['ep_count'] += 1
                    self.ep_counter +=1

            return

        

    def apply_smoothing(self):
        smooth_length(self.ln_lookup, self.ln_counter)
        smooth_grammar(self.grammar, self.ip_counter, self.ep_counter)
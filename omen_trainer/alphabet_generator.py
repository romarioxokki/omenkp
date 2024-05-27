import math


def dist(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def to_base_pattern(pattern, i, j):
    result = [(x - i, y - j) for x, y in pattern]
    return tuple(result)

def decrease_coordinates(pattern, i, j):
    result = [(x - i, y - j) for x, y in pattern]
    return tuple(result)


class AlphabetGenerator:

    def __init__(self, ngram):
        self.ngram = ngram
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
        keyboardDict = {}

        for i in range(0, len(keyboard)):
            for j in range(0, len(keyboard[i])):
                if i >= 1:
                    point = (j + 1, i)
                else:
                    point = (j, i)
                keyboardDict[keyboard[i][j]] = point

        for i in range(0, len(keyboardShift)):
            for j in range(0, len(keyboardShift[i])):
                if i >= 1:
                    point = (j + 1, i)
                else:
                    point = (j, i)
                keyboardDict[keyboardShift[i][j]] = point
        self.keyboardDictionary = keyboardDict
        self.patternDictionary = {}

    def process_password(self, password):

        if len(password) < self.ngram:
            return

        password = password.strip()
        password_list_cur = []
        point_start = self.keyboardDictionary[password[0]]

        current_start_x = point_start[0]
        current_start_y = point_start[1]
        password_list_cur += [point_start]

        for letter in password[1:]:
            point = self.keyboardDictionary[letter]
            if dist(password_list_cur[-1], point) < 2:
                password_list_cur += [point]
            else:
                if len(password_list_cur) > 1:
                    base_pattern = decrease_coordinates(password_list_cur, current_start_x, current_start_y)
                    self.patternDictionary[base_pattern] = self.patternDictionary.setdefault(base_pattern, 0) + 1
                password_list_cur = []
                current_start_x = point[0]
                current_start_y = point[1]
                password_list_cur += [point]
        if len(password_list_cur) > 1:
            base_pattern = decrease_coordinates(password_list_cur, current_start_x, current_start_y)
            self.patternDictionary[base_pattern] = self.patternDictionary.setdefault(base_pattern, 0) + 1

        return

    def get_alphabet(self, count_passwords):

        sorted_alphabet = sorted(list(self.patternDictionary.items()),key=lambda x: x[1])

        final_alphabet = []
        for key, value in sorted_alphabet:
            if value > count_passwords * 0.001:
                final_alphabet += [key]
                print(f'{key}&{value}\n')
    
        return final_alphabet


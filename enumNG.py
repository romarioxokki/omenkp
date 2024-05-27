
from __future__ import print_function
import sys


if sys.version_info[0] < 3:
    print("This program requires Python 3.x", file=sys.stderr)
    sys.exit(1)
    
import argparse
import os
import configparser

import time

from omen_cracker.input_file_io import load_rules
from omen_cracker.markov_cracker import MarkovCracker
from omen_cracker.optimizer import Optimizer
import  math



def dist(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def write_passwords_to_file(passwords, filename):
    with open(filename, 'a') as f:
        for password in passwords:
            f.write(''.join(''.join(part) for part in password) + '\n')


from itertools import product


from itertools import product

def generate_possible_sequences(sequence, keyboard_dict, keyboard_shift_dict):
    possible_sequences = []
    for sub_sequence in sequence:
        sub_sequences_list = []  # Список для хранения последовательностей символов для текущей подпоследовательности
        for x in range(0, 12):
            for y in range(0, 4):
                cur_pattern = increase_coordinates(sub_sequence, x, y)
                sub_sequence_combinations = []
                for press in cur_pattern:
                    possible_presses = []
                    if press in keyboard_dict:
                        possible_presses.append(keyboard_dict[press])
                    if press in keyboard_shift_dict:
                        possible_presses.append(keyboard_shift_dict[press])
                    sub_sequence_combinations.append(possible_presses)
                # Генерируем все возможные комбинации символов для текущей подпоследовательности
                combinations = [''.join(combination) for combination in product(*sub_sequence_combinations)]
                sub_sequences_list.extend(combinations)
        possible_sequences.append(sub_sequences_list)  # Добавляем список возможных последовательностей символов для текущей подпоследовательности
    return possible_sequences


def generate_passwords(subsequences_list, keyboard_dict):
    passwords = []  # Список для хранения всех возможных паролей
    n = len(subsequences_list)  # Количество частей пароля

    # Рекурсивная функция для построения всех возможных паролей
    def build_passwords(password, idx):
        # Если пароль содержит все части, добавляем его в список паролей
        if len(password) == n:
            passwords.append(password)
            return

        for subsequence in subsequences_list[idx]:
            # Проверяем расстояние между концом предыдущей части и началом текущей части
            if len(password) == 0 or dist(keyboard_dict[password[-1][-1]], keyboard_dict[subsequence[0]]) >= 0:
                # Рекурсивно строим пароль с добавлением текущей части
                build_passwords(password + [subsequence], idx + 1)

    # Начинаем построение паролей с первой части
    build_passwords([], 0)

    return passwords

def generate_combinations(list_of_lists):
    return [''.join(combination) for combination in product(*list_of_lists)]
# Функция для увеличения координат точек
def increase_coordinates(sub_sequence, dx, dy):
    return [(x + dx, y + dy) for x, y in sub_sequence]


def list_sequence_to_characters(sequence_list, keyboard_dict):
    characters = []
    for press in sequence_list:
        if press in keyboard_dict:
            characters.append(keyboard_dict[press])
        else:
            characters.append(press)
    return characters


def get_possible_characters(point, keyboard_dict, keyboard_shift_dict):
    if point in keyboard_dict and point in keyboard_shift_dict:
        return [keyboard_dict[point], keyboard_shift_dict[point]]
    else:
        return None

def parse_command_line(runtime_options):
    parser = argparse.ArgumentParser(description='OMEN Guess Generator: Creates password guesses')
    
    parser.add_argument('--rule','-r', help='Name of ruleset to use. Default is ' + 
        '[' + runtime_options['rule_name'] + ']',
        metavar='RULESET_NAME', required=False, default=runtime_options['rule_name'])
        
    parser.add_argument('--session','-s', help='Session name for saving/restarting a session. Default is ' + 
        '[' + runtime_options['session_name'] + ']',
        metavar='SESSION_NAME', required=False, default=runtime_options['session_name'])
        
    parser.add_argument('--restore', help='Restore the previous cracking session specified in the "--session" option',
        dest='restore', action='store_const', const = not runtime_options['restore'])
        
    parser.add_argument('--debug','-d', help='Print debugging info vs password guesses',
        dest='debug', action='store_const', const= not runtime_options['debug'])
        
    parser.add_argument('--test','-t', help='For debugging. Allows you to type in a password and will print out parse info for it',
        dest='test', action='store_const', const = not runtime_options['test'])
        
    parser.add_argument('--max_guesses','-m', help='Set a maximum number of guesses ',
        dest='max_guesses', metavar='NUM_GUESSES', required=False, type=int, default=-1)
    
    try:
        args=parser.parse_args()

        runtime_options['rule_name'] = args.rule
        runtime_options['debug'] = args.debug
        runtime_options['test'] = args.test
        runtime_options['session_name'] = args.session
        runtime_options['restore'] = args.restore
        runtime_options['max_guesses'] = args.max_guesses

    except Exception as msg:
        print(msg, file=sys.stderr)
        return False
    except SystemExit:
        return False

    return True 


def print_banner(program_details):
    print('',file=sys.stderr)
    print (program_details['program'] + " Version " + program_details['version'], file=sys.stderr)
    print ("This version written by " + program_details['author'], file=sys.stderr)
    print ("Original version writtem by the Horst Goertz Institute for IT-Security", file=sys.stderr)
    print ("Sourcecode available at " + program_details['source'], file=sys.stderr)
    print('',file=sys.stderr)  



    


def main():
    
    management_vars = {
        ##--Information about this program--##
        'program_details':{
            'program':'enumNG.py',
            'version': '0.2',
            'author':'Roman Emelyanov',
            'contact':'era002@mephi.ru',
            'source':'https://github.com/romarioxokki'
        },

        'runtime_options':{

            'rule_name':'Default',

            'debug':False,

            'test':False,

            'session_name':'default',

            'restore':False,

            'max_guesses':-1,

        }
    }  

    print_banner(management_vars['program_details'])

    command_line_results = management_vars['runtime_options']
    if parse_command_line(command_line_results) != True:
        return

    absolute_base_directory = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),'Rules',command_line_results['rule_name']
        )

    grammar = {}

    print("loading ruleset: " + command_line_results['rule_name'],file=sys.stderr)
    if not load_rules(absolute_base_directory, grammar, min_version=management_vars['program_details']['version']):
        print("Error reading the ruleset, exiting", file=sys.stderr)
        return



    ##--Initialize the TMTO optimizer
    optimizer = Optimizer(max_length = 4)
    
    ##--Initialize the Markov Cracker 
    try:    
        cracker = MarkovCracker(
            grammar = grammar, 
            version = management_vars['program_details']['version'], 
            base_directory = os.path.dirname(os.path.realpath(__file__)), 
            session_name = command_line_results['session_name'],
            rule_name = command_line_results['rule_name'],
            uuid = grammar['uuid'],
            optimizer = optimizer,
            restore = command_line_results['restore'],   
            )  
    except:
        print("Error loading the save file, exiting", file=sys.stderr)
        return

    if command_line_results['test']:
        while True:
            guess = input("Enter string to parse:")
            cracker.parse_input(guess)

    print("--Starting to generate guesses-- ",file=sys.stderr)

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
    keyboardShiftDict = {}

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
            keyboardShiftDict[keyboardShift[i][j]] = point
    reverse_keyboard_dict = {v: k for k, v in keyboardDict.items()}
    reverse_keyboard_shift_dict = {v: k for k, v in keyboardShiftDict.items()}
    try:
 
        num_guesses = 0
        
        guess, level = cracker.next_guess()
        while guess != None:
            num_guesses += 1
            if command_line_results['debug']:
                if num_guesses % 100000 == 0:
                    print()
                    print("guesses: " + str(num_guesses))
                    print("level: " + str(level))
            else:
                if num_guesses % 100000 == 0:
                    cracker.save_session()

                sub_tuples = []  # Создаем список для хранения подкортежей
                current_sub_tuple = []  # Создаем список для формирования текущего подкортежа

                # Проходим по каждому элементу в кортеже
                list_of_lists = []  # Создаем список для хранения списков кортежей
                current_sub_list = []  # Создаем список для формирования текущего подсписка

                # Проходим по каждому элементу в кортеже
                for item in guess:
                    # Если текущий элемент не равен (5, 5), добавляем его к текущему подсписку
                    if item != (5, 5):
                        current_sub_list.append(item)
                    else:
                        # Если текущий элемент равен (5, 5), добавляем текущий подсписок к списку списков и создаем новый пустой подсписок
                        list_of_lists.append(current_sub_list)
                        current_sub_list = []

                # Добавляем последний подсписок к списку списков
                if current_sub_list:
                    list_of_lists.append(current_sub_list)

                print(list_of_lists)
                possible_sequences = generate_possible_sequences(list_of_lists, reverse_keyboard_dict, reverse_keyboard_shift_dict)
                passwords = generate_combinations(possible_sequences)
                print(passwords)
                write_passwords_to_file(passwords, 'all_password.txt')

                
            if command_line_results['max_guesses'] > 0 and num_guesses >= command_line_results['max_guesses']:
                break
            guess, level = cracker.next_guess()
            
    except (KeyboardInterrupt, BrokenPipeError) as e:
        print("Halting guess generation based on Ctrl-C being detected",file=sys.stderr)
        cracker.save_session()
    
    print('', file=sys.stderr)    
    print("--Done generating guesses-- ",file=sys.stderr)

        

if __name__ == "__main__":
    main()
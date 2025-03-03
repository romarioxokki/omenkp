from __future__ import print_function
import sys
if sys.version_info[0] < 3:
    print("This program requires Python 3.x", file=sys.stderr)
    sys.exit(1)
    
import argparse
import os
import uuid

from omen_trainer.common_file_io import detect_file_encoding
from omen_trainer.alphabet_lookup import AlphabetLookup
from omen_trainer.trainer_file_io import TrainerFileIO
from omen_trainer.output_file_io import save_rules_to_disk
from omen_trainer.alphabet_generator import AlphabetGenerator

  

def is_password_valid(password, allowed_chars):
    return all(char in allowed_chars for char in password)


firstRow = "`1234567890-="
firstRowShift = "~!@#$%^&*()_+"
secondRow = "qwertyuiop[]\\"
secondRowShift = "QWERTYUIOP{}|"
thirdRow = "asdfghjkl;'"
thirdRowShift = "ASDFGHJKL:\""
fourthRow = "zxcvbnm,./"
fourthRowShift = "ZXCVBNM<>?"
allowed_chars = firstRow + firstRowShift + secondRow + secondRowShift + thirdRow + thirdRowShift + fourthRow + fourthRowShift

def parse_command_line(runtime_options):
    parser = argparse.ArgumentParser(description='OMEN Trainer: Creates n-grams for use \
        by the OMEN password guess generator')
    
    ##Input File options
    group = parser.add_argument_group('Input Files')
    group.add_argument('--training', '-t', help='The training set of passwords to train from.',
        metavar='FILENAME',required=True)
    group.add_argument('--encoding','-e', help='File encoding used to read the input training set. If not specified autodetect is used', metavar='ENCODING', required=False)
    group.add_argument('--alphabet','-a', help='Dynamically learn alphabet from training set vs using the default [a-zA-Z0-9!.*@-_$#<?]. ' +
    'Note, the size of alphabet will get up to the N most common characters. Higher values can slow down the cracker ' +
    'and increase memory requirements', type=int, metavar='SIZE_OF_ALPHABET', required=False)
    
    ##Output file options    
    group = parser.add_argument_group('Output Options')
    group.add_argument('--rule','-r', help='Name of generated ruleset. Default is ' + 
        '[' + runtime_options['rule_name'] + ']',
        metavar='RULESET_NAME', required=False, default=runtime_options['rule_name'])
    
    ##Markov grammar options    
    group = parser.add_argument_group('nGram Calculation')
    group.add_argument('--ngram','-n', help='Changes the size of the nGram n ' +
        '(possible values="2", "3", "4") Default is [' + str(runtime_options['ngram']) + ']',
        metavar='INT', required=False, type=int, choices=range(2,6), default=runtime_options['ngram'])
    
    try:
        args=parser.parse_args()
        
        ##Input File options
        runtime_options['training_file'] = args.training
        runtime_options['encoding'] = args.encoding
        
        ##Alphabet options
        runtime_options['learn_alphabet'] = args.alphabet
        ##Sanity check of values
        if args.alphabet and args.alphabet < 10:
            parser.error("Minimum alphabet size is 10 because based on past experience anything less than that is probably a typo. If this is a problem please post on the github site")
        
        ##Output file options
        runtime_options['rule_name'] = args.rule
        
        ##Markov grammar options
        runtime_options['ngram'] = args.ngram
        
    except Exception as msg:
        print(msg, file=sys.stderr)
        return False
    except SystemExit:
        return False

    return True 

    
###################################################################################
# Prints the startup banner when this tool is run
###################################################################################
def print_banner(program_details):
    print('',file=sys.stderr)
    print (program_details['program'] + " Version " + program_details['version'], file=sys.stderr)
    print ("This version written by " + program_details['author'], file=sys.stderr)
    print ("Original version writtem by the Horst Goertz Institute for IT-Security", file=sys.stderr)
    print ("Sourcecode available at " + program_details['source'], file=sys.stderr)
    print('',file=sys.stderr)  






def main():
    
    management_vars = {
        'program_details':{
            'program':'createNG.py',
            'version': '0.1',
            'author':'Emelyanov Roman',
            'contact':'era002@mephi.ru',
            'source':'https://github.com/romarioxokki'
        },
        ##--Runtime specific values, can be overriden via command line options
        'runtime_options':{
            ##training set options
            'training_file':None,
            'encoding':None,
            
            ##Output options
            'rule_name':'Default',
            
            #nGram Calculation
            'ngram':2,
            'max_level':10,
            'alphabet': [((0, 0), (-1, 0), (-1, 0), (0, 0)),
                ((0, 0), (-1, 0), (0, 1)),
                ((0, 0), (1, 1), (1, 2)),
                ((0, 0), (1, 1), (2, 0)),
                ((0, 0), (-1, -1), (-1, 0)),
                ((0, 0), (-1, 0), (0, 0), (0, 0)),
                ((0, 0), (0, -1), (1, -1), (1, -1)),
                ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0)),
                ((0, 0), (1, 0), (1, 1)),
                ((0, 0), (1, 0), (1, 0), (0, 0)),
                ((0, 0), (-1, 0), (0, 0), (-1, 0)),
                ((0, 0), (-1, 1), (0, 0)),
                ((0, 0), (1, -1), (1, -1)),
                ((0, 0), (1, 0), (1, -1)),
                ((0, 0), (1, 0), (0, 0), (1, 0)),
                ((0, 0), (0, 0), (1, 0), (1, 0)),
                ((0, 0), (0, -1), (0, 0)),
                ((0, 0), (-1, 1), (-1, 0)),
                ((0, 0), (-1, 1), (-2, 1)),
                ((0, 0), (0, 1), (1, 0)),
                ((0, 0), (0, -1), (-1, -1)),
                ((0, 0), (0, 0), (1, -1)),
                ((0, 0), (1, -1), (2, -1)),
                ((0, 0), (1, 0), (2, -1)),
                ((0, 0), (1, 0), (0, 1)),
                ((0, 0), (1, -1), (0, 0)),
                ((0, 0), (-1, -1), (-1, -1)),
                ((0, 0), (0, 0), (-1, 1)),
                ((0, 0), (0, -1), (-1, 0)),
                ((0, 0), (1, 1), (0, 0)),
                ((0, 0), (-1, 0), (-2, 1)),
                ((0, 0), (-1, 0), (-1, 1)),
                ((0, 0), (-1, -1), (-2, -1)),
                ((0, 0), (1, 0), (0, -1)),
                ((0, 0), (0, 0), (0, 0), (0, 0)),
                ((0, 0), (1, 0), (2, 1)),
                ((0, 0), (0, 0), (-1, -1)),
                ((0, 0), (1, -1), (0, -1)),
                ((0, 0), (0, 1), (-1, 0)),
                ((0, 0), (0, 0), (0, 1)),
                ((0, 0), (0, 0), (0, -1)),
                ((0, 0), (0, -1), (0, -1)),
                ((0, 0), (1, 0), (2, 0), (3, 0)),
                ((0, 0), (-1, -1), (0, 0)),
                ((0, 0), (-1, 1), (-1, 1)),
                ((0, 0), (-1, -1), (0, -1)),
                ((0, 0), (0, 1), (0, 1)),
                ((0, 0), (0, -1), (1, -1)),
                ((0, 0), (0, 1), (0, 0)),
                ((0, 0), (1, 1), (1, 1)),
                ((0, 0), (1, 1), (1, 0)),
                ((0, 0), (0, 0), (-1, 0)),
                ((0, 0), (-1, 0), (-2, 0)),
                ((0, 0), (-1, 0), (-1, 0)),
                ((0, 0), (-1, 0), (0, 0)),
                ((0, 0), (1, 0), (0, 0)),
                ((0, 0), (0, 0), (1, 0)),
                ((0, 0), (1, 0), (1, 0)),
                ((0, 0), (0, 0), (0, 0)),
                ((0, 0), (1, 0), (2, 0)),
                ((0, 0), (0, 1)),
                ((0, 0), (1, 1)),
                ((0, 0), (1, -1)),
                ((0, 0), (-1, 1)),
                ((0, 0), (-1, -1)),
                ((0, 0), (0, -1)),
                ((0, 0), (-1, 0)),
                ((0, 0), (1, 0)),
                ((0, 0), (0, 0))],
            'learn_alphabet': True,
            'smooting':None,
            
            #Options added for this version of OMEN
            'max_length':20,

        }
    }  
    
    ##--Print out banner
    print_banner(management_vars['program_details'])
    
    ##--Parse the command line ---##
    command_line_results = management_vars['runtime_options']
    if parse_command_line(command_line_results) != True:
        return
    
    ##--Set the file encoding for the training set
    ##--If NOT specified on the command line by the user run an autodetect
    if command_line_results['encoding'] == None:
        possible_file_encodings = []
        if not detect_file_encoding(command_line_results['training_file'], possible_file_encodings):
            ascii_fail()
            print("Exiting...")
            return
            
        command_line_results['encoding'] = possible_file_encodings[0]

    # command_line_results['learn_alphabet'] = True
    if command_line_results['learn_alphabet'] != None:
        print('',file=sys.stderr)
        print('---Starting first pass through training set to learn the alphabet---',file=sys.stderr)
        print('',file=sys.stderr)

        ##--Open the training file IO for the first pass to learn the Alphabet
        input_dataset = TrainerFileIO(command_line_results['training_file'], command_line_results['encoding'])
        
        ##--Initialize the alphabet generator
        ag = AlphabetGenerator(ngram = 2)
        
        ##--Now loop through all the passwords to get the character counts for the alphabet
        password = input_dataset.read_password()
        total_count = 0
        while password != None:
            if total_count % 1000000 == 0 and total_count != 0:
                print(str(total_count//1000000) +' Million', file=sys.stderr)
            if is_password_valid(password,allowed_chars):
                ag.process_password(password)
            password = input_dataset.read_password()
            total_count +=1

        command_line_results['alphabet'] = ag.get_alphabet(total_count)
        alphabet_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),'Rules',command_line_results['rule_name'],'alphabet.txt')
        file_Alphabet = open(alphabet_file, 'a')
        print(command_line_results['alphabet'])
        for pattern in command_line_results['alphabet']:

            file_Alphabet.write(f'{pattern}\n')
        file_Alphabet.close()
        print("Done learning alphabet", file=sys.stderr)
        print("Displaying learned alphabet to a console usually ends poorly for non-standard characters.", file=sys.stderr)
        print("If you want to review what the alphabet actually is you can view it at: " + alphabet_file, file=sys.stderr)
    
    else:
        print("Using Default Alphabet", file=sys.stderr)
    
    print("", file=sys.stderr)
    
    ##--Initialize lookup tables
    omen_trainer = AlphabetLookup(
        alphabet = command_line_results['alphabet'], 
        ngram = 2,
        max_length = command_line_results['max_length']
        )

    ##--Initialize the trainer file io
    input_dataset = TrainerFileIO(command_line_results['training_file'], command_line_results['encoding'])

    
    print("--Starting to parse passwords--",file=sys.stderr)
    print("Passwords parsed so far (in millions): ", file=sys.stderr)    
    ##--Go through every password
    password = input_dataset.read_password()
    total_count = 0
    while password != None:
        ##--Print out status info
        if total_count % 1000000 == 0 and total_count != 0:
            print(str(total_count//1000000) +' Million', file=sys.stderr)
        if is_password_valid(password, allowed_chars):
            omen_trainer.parse(password)
        password = input_dataset.read_password()
        total_count +=1
    print("Done with intial parsing.", file=sys.stderr)
    print("Number of passwords trained on: " + str(total_count), file=sys.stderr)
    print("Number of file encoding errors = " + str(input_dataset.num_encoding_errors), file=sys.stderr)
    print()
    print("--Applying probability smoothing--", file=sys.stderr)
    # for key,value in omen_trainer.grammar.items():
    #     print(key,value)
    # raise Exception(omen_trainer.grammar.items())
    omen_trainer.apply_smoothing()
    
    print("--Saving Results--", file=sys.stderr)
    
    ####################
    ##--Save the results
    ####################
    
    # Get the absolute path in case this program is run from another dirctory
    absolute_base_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),'Rules',command_line_results['rule_name'])
    
    ##--This will be the config that is actually written to disk
    config_info = {
        'program_details':management_vars['program_details'],
        'training_settings': {
            'training_file':command_line_results['training_file'],
            'alphabet_encoding':command_line_results['encoding'],
            'ngram':command_line_results['ngram'],
            'max_level':10,
            'uuid':str(uuid.uuid4()),
            },
    }
    
    ##--Bundle everything to send to the "save_rules_to_disk" function
    save_info = {
        "rule_directory":absolute_base_directory,
        "ngrams":omen_trainer,
        }

    #print(omen_trainer.grammar)
    try:
        save_rules_to_disk(omen_trainer, save_info, config_info)
        
    except IOError as error:
        print ("Error saving rules", file=sys.stderr)
        print ("Error is " + str(error), file=sys.stderr)
        print ("The OMEN training data likely was not saved to disk", file=sys.stderr)
        return
    
    print()    
    print("Done! Enjoy cracking passwords with OMEN!", file=sys.stderr)
    print("To use this training set to crack, make sure you use the following option in enumNG:", file=sys.stderr)
    print("    '-r " +command_line_results['rule_name'] + "'" , file=sys.stderr)
  


#######################################################################
# Standard python stub to call main
#######################################################################  
if __name__ == "__main__":
    main()


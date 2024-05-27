#!/usr/bin/env python3

#########################################################################
# Handles probability smoothing for a given grammar
# Breaking this out into its own section to make changing this at
# a later point easier
#
#########################################################################

import sys
import math

####################################################################################################
## Responsible for applying probability smoothing to the grammar
##
##  Will update the grammar and return it with the levels assicated with each transition
##
##--The input grammar has the format (example for ngram=4)--##
##   {
##       'aaa': {       //the starting charaters
##           ip_count: 5,    //the number of times they have shown up in the ip (begining)
##           ep_count: 3,    //the number of times they have shown up in the ep (end)
##           cp_count: 100,  //the number of times they have shown up total in passwords (for cp)
##           next_letter:{   //the next letter for cp
##             a:5           //represents the cp 'aaaa' with the count of the times that cp has been seen
##             b:12,         //represents the cp 'aaab'
##             ...,
##           },
##       },
##       ...,
##   }
##
##--The output grammar will have the following format (example for ngram=4)--##
##   {
##       'aaa': {       //the starting charaters
##           ip_count: 5,    //the number of times they have shown up in the ip (begining)
##           ip_level: 2,    //the smoothed level for the ip
##           ep_count: 3,    //the number of times they have shown up in the ep (end)
##           ep_level: 5,    //The smoothed level for the ep
##           cp_count: 100,  //the number of times they have shown up total in passwords (for cp)
##           next_letter:{   //the next letter for cp
##             a:(1,5)       //represents the cp 'aaaa' with smoothed level 1, seen 5 times
##             b:(0,12),     //represents the cp 'aaab' with smoothed level 0, seen 12 times
##             ...,
##           },
##       },
##       ...,
##   }
##########################################################################################################
def smooth_grammar(grammar, ip_total, ep_total):
    
    ##--Set the level adjust factor for smoothing
    ##--May eventually move this to a configurable options
    level_adjust_factor = {
        'ip':250,
        'cp':2,
        'ep':250,
        }
    
    ##--Loop through the top (ngram-1) list that has IP, EP and the next letter transition   
    for starting_letters in grammar.keys():
        
        ##--Saving a pointer to the dic to clean up code
        index = grammar[starting_letters]
        
        ##--Save the IP info
        index['ip_level'] = _calc_level(index['ip_count'], ip_total, level_adjust_factor['ip'])
        
        ##--Save the EP info
        index['ep_level'] = _calc_level(index['ep_count'], ep_total, level_adjust_factor['ep'])
        
        ##--Now loop through all the conditional probabilities
        for cp in index['next_letter']:
            ##--Saving a pointer to the dic to clean up code
            cp_index = index['next_letter'][cp]
            
            saved_level = _calc_level(cp_index, index['cp_count'], level_adjust_factor['cp'])
            
            index['next_letter'][cp] = (saved_level, cp_index)


######################################################################################################
# Responsible for smoothing the length info
# Given a list of the lengths with their associated counts, return a list of the lengths
# with the (level, count)
######################################################################################################
def smooth_length(ln_lookup, ln_counter, max_level = 10):
        
    ##--Smooth the level lengths
    for length, count in enumerate(ln_lookup): 
        
        ##--Calculate the level
        level = _calc_level(count, ln_counter, 1)
        
        ln_lookup[length] = (level, count)
        
    
########################################################################################################
# Actually applies the probability smoothing levels
# Returns the calculated level
# Note, if total count is 0 will intentionally raise a divide by 0 error
########################################################################################################            
def _calc_level(base_count, total_count, level_adjust_factor, max_level = 10):

    probi = base_count / total_count
    probi *= level_adjust_factor
    probi += 0.00000000001

    level = math.floor(-1 * math.log(probi))

    if level > max_level:
        level = max_level

    elif level < 0:
        level = 0

    return level

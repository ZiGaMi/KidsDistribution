# ===============================================================================
# @file:    main.py
# @note:    This script is part of kids distribution program
# @author:  Ziga Miklosic
# @date:    25.08.2021
# @brief:   Scirpt for determine of kids distribution based on its year
# ===============================================================================

# ===============================================================================
#       IMPORTS  
# ===============================================================================
import os
import sys
import time
from tabulate import tabulate
import copy

# ===============================================================================
#       CONSTANTS
# ===============================================================================

## Current year of analysis
CURRENT_YEAR = 2021

## Number of groups is zero
#
# @note This must be a prime number in order to hide information
#       of possible combination in end table
GROUP_ZERO_MAGIC_NUM = 57

# ===============================================================================
#       FUNCTIONS
# ===============================================================================

# ===============================================================================
#       CLASSES
# ===============================================================================

# ===============================================================================
# @brief:   POPULATION
#
#    Population of all kids generations
#
# ===============================================================================
class KidsPopulation:

    # Types of group
    HOMOGENE_GROUPE     = { "name": "Homogen",      "weight": 1 }
    HETEROGENE_GROUPE   = { "name": "Heterogen",    "weight": 2 }
    COMBINATION_GROUPE  = { "name": "Kombiniran",   "weight": 3 }

    # ===============================================================================
    # @brief:   Create kids population
    #
    # @param[in]:   current_year - Current year of distribution process
    # @return:      void
    # ===============================================================================  
    def __init__(self, current_year):
        self.pop =  {   "Letnik":   [],
                        "Stevilo":  [],
                        "Starost":  []
                    }
        self.current_year = current_year
        
    # ===============================================================================
    # @brief:   Add kids year to population
    #
    # @param[in]:   year            - Year of kids, must be less or qual to current year
    # @param[in]:   num_of_kids     - Number of kids that fullfill certain condition
    # @return:      void
    # ===============================================================================  
    def add(self, year, num_of_kids):
        self.pop["Letnik"].append( year )
        self.pop["Stevilo"].append( num_of_kids )
        self.pop["Starost"].append( self.current_year - year )

    # ===============================================================================
    # @brief:   Print out kids population
    #
    # @return:      pvoid
    # ===============================================================================  
    def print(self):
        print( tabulate(self.pop, headers='keys', tablefmt='fancy_grid', showindex=True))

    def get_num_of_kids_by_age_range(self, min, max):
        num_of = 0

        for idx, age in enumerate( self.pop["Starost"] ):
            if ( age >= min ) and ( age <= max ):
                num_of += self.pop["Stevilo"][idx]

        return num_of

    def get_num_of_kids_by_age_specific(self, years):
        num_of = 0

        for idx, age in enumerate( self.pop["Starost"] ):
            if age in years:
                num_of += self.pop["Stevilo"][idx]

        return num_of
    

# ===============================================================================
# @brief:   Intermediate table
#
#   Based on intermediate table later evaluation of best fit to groupe
#   will be done. 
# 
#   This table is basis for later analysis and evaluations of best results.
#   
# ===============================================================================
class IntermediateTable(KidsPopulation):

    # ===============================================================================
    # @brief:   Create distribution table
    #
    # @param[in]:   pop - Kids population
    # @return:      void
    # ===============================================================================  
    def __init__(self, pop):
        self.table = {  "Tip":                  [],
                        "Posebnost":            [],
                        "Starostni razred":     [],
                        "Velikosti razred":     [],
                        "Stevilo otrok":        [],
                        "Distribucija otrok":   [],
                        "Stevilo oddelkov":     [],
                        "Rezultat":             [],
                        }
        
        self.kids = pop

    # ===============================================================================
    # @brief:   Add new case to table
    #
    # @param[in]:   type            - Type of groupe (homogen, heterogen, combination)
    # @param[in]:   years           - Array of years as a target groupe
    # @param[in]:   size_of_groupe  - Array of groupe [min,max] childs
    # @param[in]:   exception       - Number of exception
    # @return:      void
    # ===============================================================================  
    def add(self, type, years, size_of_groupe, exception=None):
        
        # Calculate number of kids
        num_of_kids = self.kids.get_num_of_kids_by_age_specific( years )

        # Calculate distribution
        dist_of_kids = self.__calc_distribution( years )

        # Calculate number of groups
        num_of_groups, num_of_remains = self.__calc_num_of_groups__( size_of_groupe, num_of_kids )

        # Determine result
        result = self.__calc_result__( type, num_of_groups, num_of_remains, exception )

        # Fill table
        self.table["Tip"].append(type["name"])
        self.table["Posebnost"].append(exception)
        self.table["Starostni razred"].append(years)
        self.table["Velikosti razred"].append(size_of_groupe)
        self.table["Stevilo otrok"].append( num_of_kids )
        self.table["Distribucija otrok"].append( dist_of_kids )
        self.table["Stevilo oddelkov"].append( "%d (%s)" % ( num_of_groups, num_of_remains ))
        self.table["Rezultat"].append( "%s" % ( result ))

    # ===============================================================================
    # @brief:   Print out distributioon table
    #
    # @return:      pvoid
    # ===============================================================================  
    def print(self):
        print(tabulate(self.table, headers='keys', tablefmt='fancy_grid', showindex=True, numalign="center", stralign="left"))

    # ===============================================================================
    # @brief:   Calculate number of groups and remains
    #
    # @param[in]:   size_of_groupe  - Limits of groupe [min, max]
    # @param[in]:   num_of_kids     - Number of kids that fullfill certain condition
    # @return:      num_of_sec      - Number of groups
    # @return:      num_of_remains  - Number of remains kids
    # ===============================================================================  
    def __calc_num_of_groups__(self, size_of_groupe, num_of_kids):
        num_of_sec = 0
        num_of_remains = 0
        
        min = int( size_of_groupe[0] )
        max = int( size_of_groupe[1] )

        # Calculate number of groups
        num_of_sec = int( num_of_kids / min )

        # Calculate remains - too much for groupe
        if num_of_sec == 0:
            num_of_remains = num_of_kids % max

        # More groupe
        else:
            num_of_kids -= num_of_sec * max

            if num_of_kids < 0:
                num_of_remains = 0
            else:
                num_of_remains = num_of_kids % max

        return num_of_sec, num_of_remains

    # ===============================================================================
    # @brief:   Calculate distribution of childs age
    #
    # @param[in]:   years   - Target years of childs
    # @return:      dist    - Distribution of kids in target years
    # ===============================================================================  
    def __calc_distribution(self, years):
        dist = []
        
        for age in range(7):
            if age in years:
                dist.append( self.kids.get_num_of_kids_by_age_specific( [age] ))
            else:
                dist.append( 0 )
        
        return dist

    # ===============================================================================
    # @brief:   Evaluation of case
    #
    #       Based on number of groups and kids remains determine the result if
    #       this groupe can be feasable or not.
    #
    # @param[in]:   num_of_groupe   - Number of possible groups
    # @param[in]:   num_of_remains  - Number of remains child
    # @return:      resutl          - Result of evaluation
    # ===============================================================================  
    def __calc_result__(self, type, num_of_groups, num_of_remains, exception):
        result = 1

        # Apply type of groupe
        result *= type["weight"]

        # Apply number of groups
        if num_of_groups == 0:
            result *= GROUP_ZERO_MAGIC_NUM
        else:
            result *= num_of_groups

        # Apply number of remains
        result *= ( 2*num_of_remains + 1 )

        # Apply exception
        # NOTE: Exception is wanted!
        if exception is not None:
            result *= 0.5

        return result
    
    def get_type(self, idx):
        return self.table["Tip"][idx]
    
    def get_years(self, idx):
        return self.table["Starostni razred"][idx]

    def is_homogene_type(self, idx):
        if self.get_type(idx) == self.HOMOGENE_GROUPE["name"]:
            return True
        else:
            return False

    def is_heterogene_type(self, idx):
        if self.get_type(idx) == self.HETEROGENE_GROUPE["name"]:
            return True
        else:
            return False

    def is_combination_type(self, idx):
        if self.get_type(idx) == self.COMBINATION_GROUPE["name"]:
            return True
        else:
            return False

    def get_result(self, idx):
        return float(self.table["Rezultat"][idx])



# ===============================================================================
# @brief:   End table
#
#   End table row contains all combinations of groups from intermediate table that
#   obtains whole kids generations, meaning all years.
#   
#   Results of this table means best possible combination of kids
#   
# ===============================================================================
class EndTable(IntermediateTable):

    # ===============================================================================
    # @brief:   Create end table
    #
    # @param[in]:   intermediate_table - Intermediate population
    # @return:      void
    # ===============================================================================  
    def __init__(self, intermediate_table):
        self.end_table = {  "Kombinacija let otrok":        [],
                            "Koncni rezultat":              [],
                            "Št. homogenih sk.":            [],
                            "Št. heterogenih sk.":          [],
                            "Št. kombiniranih sk.":         [],
                           # "Homogena sk. po letih":        [],
                            #"Heterogena sk. po letih":      [],
                           # "Kombinirana sk. po letih":     [],
                        }
        
        self.intermediate_table = intermediate_table


    def add(self, int_table_idx):
        
        years = []
        result = 0
        num_of_homogen = 0
        num_of_heterogen = 0
        num_of_combination = 0
        homogen_years = []
        heterogen_years = []
        combination_years = []

        for idx in int_table_idx:
            #self.end_table["Kombinacija let otrok"].append( self.intermediate_table.get_years(idx) )
            years.append( self.intermediate_table.get_years(idx) )

            if self.intermediate_table.is_homogene_type( idx ):
                num_of_homogen += 1
                #homogen_years.append(self.intermediate_table.get_years(idx))
            elif self.intermediate_table.is_heterogene_type(idx):
                num_of_heterogen += 1
                #heterogen_years.append(self.intermediate_table.get_years(idx))
            elif self.intermediate_table.is_combination_type(idx):
                num_of_combination += 1
                #combination_years.append(self.intermediate_table.get_years(idx))

            # Sum result 
            result += self.intermediate_table.get_result(idx)
        
        # Calculate end result
        result = result / len( int_table_idx )

        # Save years
        self.end_table["Kombinacija let otrok"].append( years )

        # Save result
        self.end_table["Koncni rezultat"].append( result )

        # Save number of each groupe type
        self.end_table["Št. homogenih sk."].append( num_of_homogen )
        self.end_table["Št. heterogenih sk."].append( num_of_heterogen )
        self.end_table["Št. kombiniranih sk."].append( num_of_combination )

        #self.end_table["Homogena sk. po letih"].append( homogen_years )
        #self.end_table["Heterogena sk. po letih"].append( heterogen_years )
        #self.end_table["Kombinirana sk. po letih"].append( combination_years )

    def print(self):
        print(tabulate(self.end_table, headers='keys', tablefmt='fancy_grid', showindex=True, numalign="center", stralign="left"))


# ===============================================================================
#       FUNCTIONS
# ===============================================================================


# ===============================================================================
#       MAIN ENTRY
# ===============================================================================
if __name__ == "__main__":

    # All the kids
    kids = KidsPopulation( CURRENT_YEAR )

    # Generate population
    kids.add( 2021, 5 )
    kids.add( 2020, 8 )
    kids.add( 2019, 15 )
    kids.add( 2018, 11 )
    kids.add( 2017, 24 )
    kids.add( 2016, 15 )
    kids.add( 2015, 1 )
    kids.add( 2014, 0 )

    # Show kids population
    kids.print()
    
    # Create intermediate table for calculation and evaluation purposes
    int_table = IntermediateTable( kids )
    
    # ==========================================================================================
    # Add all posible combination of kids groups based on year and size of groupe criteria
    # ==========================================================================================
    #           Type                        Years                   Grupe limits     
    int_table.add(  kids.HOMOGENE_GROUPE,      [0,1],                  [9,12]       );
    int_table.add(  kids.HOMOGENE_GROUPE,      [1,2],                  [9,12]       );
    int_table.add(  kids.HOMOGENE_GROUPE,      [0,0],                  [9,12]       );
    int_table.add(  kids.HOMOGENE_GROUPE,      [1,1],                  [9,12]       );
    int_table.add(  kids.HOMOGENE_GROUPE,      [2,2],                  [9,12]       );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3,4],                  [12,17]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [4,5],                  [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [5,6],                  [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [6,7],                  [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3],                    [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [4],                    [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [5],                    [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [6],                    [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [7],                    [17,22]      );
    int_table.add(  kids.HOMOGENE_GROUPE,      [0,1,2],                [9,12],      exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3,4,5],                [12,17],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3,4,5],                [17,22],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6],              [12,17],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6],              [17,22],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6,7],            [12,17],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6,7],            [17,22],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [4,5,6],                [17,22],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [4,5,6,7],              [17,12],     exception=1   );
    int_table.add(  kids.HOMOGENE_GROUPE,      [5,6,7],                [17,22],     exception=1   );
    int_table.add(  kids.HETEROGENE_GROUPE,    [0,1,2],                [7,10]      );
    int_table.add(  kids.HETEROGENE_GROUPE,    [3,4,5,6,7],            [14,19]     );
    int_table.add(  kids.COMBINATION_GROUPE,   [0,1,2,3,4,5,6,7],      [10,17]     );
    
    # Add more here if needed...

    # Show intermediate table
    print("")
    print("*******************************************************************************************************")
    print("     INTERMEDIATE TABLE")
    print("*******************************************************************************************************")
    print("")
    int_table.print()

    # Create end table
    end_table = EndTable( int_table )

    # ==========================================================================================
    # Add all posible combination of kids year groups to create generations
    # ==========================================================================================
    #               Intermediate table row idx   
    
    # Only homogen types
    end_table.add( [0,1,5,6,7,8] )
    end_table.add( [2,3,4,5,6,7,8] )

    # Only heterogene types
    end_table.add( [24,25] )

    # Combination of homogene & heterogene
    end_table.add( [24, 19] )


    # Show end table
    print("")
    print("*******************************************************************************************************")
    print("     END TABLE")
    print("*******************************************************************************************************")
    print("")
    end_table.print()

    # Wait prompt
    input("Press ENTER to exit...")


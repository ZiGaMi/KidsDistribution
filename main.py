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
        result = self.__evaluate_case__( num_of_groups, num_of_remains )

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
    def __evaluate_case__(self, num_of_groups, num_of_remains):

        if num_of_groups == 0:
            return "PREMALO OTROK"
        else:
            if num_of_remains == 0:
                return "POPOLNA RAZPOREDITEV"
            else:
                return "PREVEC OTROK: %s otrok je prevec in jih ni moc dodati v oddelke!" % num_of_remains



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
    table = IntermediateTable( kids )
    
    # ==========================================================================================
    # Add all posible combination of kids groups based on year and size of groupe criteria
    # ==========================================================================================
    #           Type                        Years                   Grupe limits     
    table.add(  kids.HOMOGENE_GROUPE,      [0,1],                  [9,12]       );
    table.add(  kids.HOMOGENE_GROUPE,      [1,2],                  [9,12]       );
    table.add(  kids.HOMOGENE_GROUPE,      [0,0],                  [9,12]       );
    table.add(  kids.HOMOGENE_GROUPE,      [1,1],                  [9,12]       );
    table.add(  kids.HOMOGENE_GROUPE,      [2,2],                  [9,12]       );
    table.add(  kids.HOMOGENE_GROUPE,      [3,4],                  [12,17]      );
    table.add(  kids.HOMOGENE_GROUPE,      [4,5],                  [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [5,6],                  [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [6,7],                  [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [3],                    [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [4],                    [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [5],                    [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [6],                    [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [7],                    [17,22]      );
    table.add(  kids.HOMOGENE_GROUPE,      [0,1,2],                [9,12],      exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [3,4,5],                [12,17],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [3,4,5],                [17,22],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6],              [12,17],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6],              [17,22],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6,7],            [12,17],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [3,4,5,6,7],            [17,22],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [4,5,6],                [17,22],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [4,5,6,7],              [17,12],     exception=1   );
    table.add(  kids.HOMOGENE_GROUPE,      [5,6,7],                [17,22],     exception=1   );
    table.add(  kids.HETEROGENE_GROUPE,    [0,1,2],                [7,10]      );
    table.add(  kids.HETEROGENE_GROUPE,    [3,4,5,6,7],            [14,19]     );
    table.add(  kids.COMBINATION_GROUPE,   [0,1,2,3,4,5,6,7],      [10,17]     );
    
    # Add more here if needed...

    # Show distributiom table
    table.print()

    # Wait prompt
    input("Press ENTER to exit...")


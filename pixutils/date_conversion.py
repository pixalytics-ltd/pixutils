# 
#     Performs conversions from julian day (more correct term is day of year) to year,month,date and in the other direction.
    
#     Arguments:
#        Jday = day(Year,Month,Day)
#        Year,Month,Day = day(Year,Jday)

#     Created by Samantha Lavender, June 2017.
#     Copyright © 2017 Pixalytics Ltd. All rights reserved.

import datetime

def is_leap_year(year):
#   if year is a leap year return True else return False
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0

def doy(Y,M,D):
# given year, month, day return day of year
# Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    N = int((275 * M) / 9.0) - K * int((M + 9) / 12.0) + D - 30
    return N

def ymd(Y,N):
# given year = Y and day of year = N, return year, month, day
# Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """    
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    M = int((9 * (K + N)) / 275.0 + 0.98)
    if N < 32:
        M = 1
    D = N - int((275 * M) / 9.0) + K * int((M + 9) / 12.0) + 30
    return Y, M, D



def main():
  print("Running: read_aoc")
  print("Finished")

if __name__ == "__main__":
    main()


#EOF

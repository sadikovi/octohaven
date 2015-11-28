#!/usr/bin/env python

import re
from datetime import datetime
from types import IntType
from utils import *

# mapping of week day names to numbers
WEEKDAYS = {"MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6, "SUN": 7}
# mapping of months to numbers
MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9,
    "OCT": 10, "NOV": 11, "DEC": 12}

# CrontTab class resolves Cron expression and compares current time to expression whether it
# matches it or not. Information on a subject: https://en.wikipedia.org/wiki/Cron#CRON_expression
# Schema of expression
# +--------+------+------------------+-------------------+-----------------+------+
# | Minute | Hour | Day Of The Month | Month Of The Year | Day Of The Week | Year |
# +--------+------+------------------+-------------------+-----------------+------+
#
# Some examples:
# 0 9 * * * * - every day at 09:00
# 0 8-10 * * * * - every day at 09:00
# 0 9 1-7 * 1 * - Mon if it is 1,2,3,4,5,6,7 at 09:00
#
class CronTab(object):
    def __init__(self, pattern, minute, hour, day, month, weekday, year):
        # actual raw pattern
        self.pattern = pattern
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month
        self.weekday = weekday
        self.year = year

    # resolve each part, it can have three values: star, range, single value
    @classmethod
    def resolve(cls, part, rng, alter=None):
        part = part.upper()
        rng = set(rng)
        # resolve star pattern
        if part == "*":
            return None
        # resolve ranges "," / "-" / "/"
        elif part.find(",") >= 0:
            values = part.split(",")
            arr = set()
            for x in values:
                if x.isdigit():
                    arr.add(int(x))
                elif alter and x in alter:
                    arr.add(alter[x])
                else:
                    raise StandardError("Unrecognized key: %s" % x)
            return cls.validateRange(arr, rng, part)
        elif part.find("-") >= 0:
            values = part.split("-")
            if len(values) != 2:
                raise StandardError("Cannot parse range in 'x-y' expression: %s" % part)
            mint, maxt = values[0], values[1]
            if mint.isdigit() and maxt.isdigit():
                mint, maxt = int(mint), int(maxt)
            elif not mint.isdigit() and not maxt.isdigit() and alter:
                if mint not in alter:
                    raise StandardError("Unrecognized min key: %s" % part)
                if maxt not in alter:
                    raise StandardError("Unrecognized max key: %s" % part)
                mint = alter[mint]
                maxt = alter[maxt]
            else:
                raise StandardError("Cannot parse range in 'x-y' expression: %s" % part)
            arr = set(range(mint, maxt + 1))
            return cls.validateRange(arr, rng, part)
        elif part.find("/") >= 0:
            values = part.split("/")
            if len(values) != 2 or values[0] != "*":
                raise StandardError("Cannot parse range '*/x' expression: %s" % part)
            delim = int(values[1])
            arr = set([x for x in rng if x % delim == 0])
            return cls.validateRange(arr, rng, part)
        # assume that at this stage value is a single parameter
        if part.isdigit():
            value = int(part)
        elif alter and part in alter:
            value = alter[part]
        else:
            raise StandardError("Cannot parse single value expression: %s" % part)
        if value not in rng:
            raise StandardError("Out of range: %s" % value)
        return value

    @classmethod
    def validateRange(cls, arr, rng, part):
        if not arr.issubset(rng):
            raise StandardError("Out of range: %s for %s" % (arr.difference(rng), part))
        res = arr.intersection(rng)
        if len(res) == 0:
            raise StandardError("Pattern is invalid or may result in 0 matches")
        return res

    # compare value with parsed expression for situations where it is a star, single value or range
    @private
    def compare(self, value, expression):
        if expression is None:
            return True
        if type(expression) is IntType:
            return value == expression
        if type(expression) is set:
            return value in expression
        return False

    # returns True, if timestamp matches pattern. Timestamp is in milliseconds
    def ismatch(self, timestamp):
        date = datetime.utcfromtimestamp(timestamp / 1000)
        # time parameters
        return self.compare(date.minute, self.minute) and self.compare(date.hour, self.hour) and \
            self.compare(date.day, self.day) and self.compare(date.month, self.month) and \
            self.compare(date.isoweekday(), self.weekday) and self.compare(date.year, self.year)

    def toDict(self):
        return {
            "pattern": self.pattern,
            "minute": self.minute,
            "hour": self.hour,
            "day": self.day,
            "month": self.month,
            "weekday": self.weekday,
            "year": self.year
        }

    @classmethod
    def fromDict(cls, obj):
        pattern = obj["pattern"]
        minute = obj["minute"]
        hour = obj["hour"]
        day = obj["day"]
        month = obj["month"]
        weekday = obj["weekday"]
        year = obj["year"]
        return cls(pattern, minute, hour, day, month, weekday, year)

    @classmethod
    def fromPattern(cls, pattern):
        arr = str(pattern).split()
        if len(arr) != 6:
            raise StandardError("Cannot parse pattern %s" % pattern)
        minute = cls.resolve(arr[0], range(0, 60))
        hour = cls.resolve(arr[1], range(0, 24))
        day = cls.resolve(arr[2], range(1, 32))
        month = cls.resolve(arr[3], range(1, 13), MONTHS)
        weekday = cls.resolve(arr[4], range(1, 8), WEEKDAYS)
        year = cls.resolve(arr[5], range(2014, 2032))
        return cls(pattern, minute, hour, day, month, weekday, year)

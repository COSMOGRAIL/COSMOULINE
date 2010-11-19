from datetime import timedelta

# Set this to the language you want to use.
LANG = "en"

# Singular and plural forms of time units in your language.
unit_names = dict(en = {"year" : ("year", "years"),
                        "month" : ("month", "months"),
                        "week" : ("week", "weeks"),
                        "day" : ("day", "days"),
                        "hour" : ("hour", "hours"),
                        "minute" : ("minute", "minutes"),
                        "second" : ("second", "seconds")})
                  
num_repr = dict(en = {1 : "one",
                      2 : "two",
                      3 : "three",
                      4 : "four",
                      5 : "five",
                      6 : "six",
                      7 : "seven",
                      8 : "eight",
                      9 : "nine",
                      10 : "ten",
                      11 : "eleven",
                      12 : "twelve"})

def amount_to_str(amount, unit_name):
    if amount in num_repr[LANG]:
        return num_repr[LANG][amount]
    return str(amount)

def seconds_in_units(seconds):
    """
    Returns a tuple containing the most appropriate unit for the
    number of seconds supplied and the value in that units form.

        >>> seconds_in_units(7700)
        (2, 'hour')
    """
    unit_limits = [("year", 365 * 24 * 3600),
                   ("month", 30 * 24 * 3600),
                   ("week", 7 * 24 * 3600),
                   ("day", 24 * 3600),
                   ("hour", 3600),
                   ("minute", 60)]
    for unit_name, limit in unit_limits:
        if seconds >= limit:
            amount = int(round(float(seconds) / limit))
            return amount, unit_name
    return seconds, "second"

def stringify(td):
    """
    Converts a timedelta into a nicely readable string.

        >>> td = timedelta(days = 77, seconds = 5)
        >>> print readable_timedelta(td)
        two months
    """
    seconds = td.days * 3600 * 24 + td.seconds
    amount, unit_name = seconds_in_units(seconds)

    # Localize it.
    i18n_amount = amount_to_str(amount, unit_name)
    i18n_unit = unit_names[LANG][unit_name][1]
    if amount == 1:
        i18n_unit = unit_names[LANG][unit_name][0]
    return "%s %s" % (i18n_amount, i18n_unit)
    
def test(td):
    if td.days > 100:
        fmt = "In %s, it's a long time. (%s)"
    elif td.days > 4:
        fmt = "I've only got %s to finish the project. (%s)"
    elif td.days > 0:
        fmt = "The party was %s ago. (%s)"
    elif td.seconds > 3600:
        fmt = "Something weird happened %s ago. (%s)"
    elif td.seconds > 60:
        fmt = "The train arrives in %s. (%s)"
    else:
        fmt = "%s passes fast. (%s)"
    print fmt % (stringify(td), str(td))

def main():
    global LANG
    LANG = "en"
    test(timedelta(weeks = 7, days = 3))
    test(timedelta(weeks = 1))
    test(timedelta(days = 1000))
    test(timedelta(days = 400))
    test(timedelta(days = 4))
    test(timedelta(seconds = 2000))
    test(timedelta(seconds = 9888))
    test(timedelta(seconds = 999888))
    test(timedelta(seconds = 999))
    test(timedelta(seconds = 99))
    test(timedelta(seconds = 45))
    test(timedelta(seconds = 3))

if __name__ == "__main__":
    main()
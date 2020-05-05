from datetime import datetime, timedelta

def count_workout_streak(workouts):
    """Count the number of consecutive days that the person has entered a workouts.

    :param workouts: dictionary of workout dicts
    :return: streak (str(integer))
    """
    # Initialize streak counter
    streak = 0

    # Make sure workouts are sorted
    workout_keys = list(workouts.keys())
    # Sort workouts by date then reverse (we want youngest dates at the start)
    workout_keys.sort(key=lambda value: datetime.strptime(workouts[value]['date'], "%m/%d/%Y"))
    workout_keys = workout_keys[::-1]


    # Get the current date so we can compare to the workout dates
    dtc = datetime.now()  # dtc is "Date To Check"
    delta = timedelta(days=1)

    first_workout_date = workouts[workout_keys[0]]['date']
    fwdt = datetime.strptime(first_workout_date,"%m/%d/%Y")  # fwdt = "First Workout DateTime"

    # If they have worked out today, add one
    if dtc.day == fwdt.day and dtc.month == fwdt.month and dtc.year == fwdt.year:
        streak += 1
    # If they worked out yesterday, start the streak from yesterday
    if (dtc - delta).day == fwdt.day and (dtc-delta).month == fwdt.month and (dtc-delta).year == fwdt.year:
        streak += 1
        dtc = dtc-delta
    # Loop through 2nd -> last workouts
    # For each workout, add 1 if it was the next day
    pwdt = fwdt # pwdt = "Previous Workout Date Time"
    for workout_key in workout_keys[1:]:
        workout = workouts[workout_key]
        workout_date = workout['date']
        wdt = datetime.strptime(workout_date,"%m/%d/%Y")  # "wdt = "Workout DateTime"
        if wdt.day == pwdt.day and wdt.month == pwdt.month and wdt.year == pwdt.year:
            # They logged two workouts on the same day, don't count the streak and don't move to next day
            continue
        dtc = dtc - delta
        if dtc.day == wdt.day and dtc.month == wdt.month and dtc.year == wdt.year:
            streak += 1
        pwdt = wdt

    return str(streak)

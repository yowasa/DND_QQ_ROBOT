from datetime import datetime
nowyear = datetime.now().year
nowmonth = datetime.now().month
zhou=datetime.now().isocalendar()[2]
print(zhou)
import billboard
import datetime

date = datetime.datetime.now().strftime ("%Y-%m-%d")
chart = billboard.ChartData('hot-100', date=date)

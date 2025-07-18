import sys
print(sys.executable)

update_mode = "both"
if len(sys.argv) > 1:
    if sys.argv[1] == "--update":
        update_mode = sys.argv[2]  # "day", "minute", or "both"

import schedule
import time
import subprocess
from datetime import datetime

def update_minute():
    print(f"Running minute update at {datetime.now()}")
    subprocess.run(["python", "Database_population.py", "--update", "minute"])

def update_day():
    print(f"Running day update at {datetime.now()}")
    subprocess.run(["python", "Database_population.py", "--update", "day"])

# Schedule minute updates every 5 minutes
schedule.every(5).minutes.do(update_minute)

# Schedule day update at 9:15am)
schedule.every().day.at("09:15").do(update_day) 
schedule.every().day.at("15:42").do(update_day)

while True:
    schedule.run_pending()
    time.sleep(1)

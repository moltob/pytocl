import os
import glob

def get_newest_drivelog():
    newest = max(glob.iglob('drivelogs/*.pickle'), key=os.path.getctime)
    return newest



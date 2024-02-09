import time
from datetime import datetime

now = datetime.now()
print(now.strftime("%Y-%d-%mT%H:%M:%SZ"))
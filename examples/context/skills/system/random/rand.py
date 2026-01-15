import sys
import random

try:
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    print(random.randint(a, b))
except:
    print("Usage: rand.py min max")

import sys

try:
    a = float(sys.argv[1])
    b = float(sys.argv[2])
    if a == 0:
        print("Error: 'a' cannot be 0")
    else:
        print(f"x = {-b/a}")
except Exception as e:
    print(f"Error: {e}")

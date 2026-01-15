import sys

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

try:
    n = int(sys.argv[1])
    print(f"{n} is prime: {is_prime(n)}")
except Exception as e:
    print(f"Error: {e}")

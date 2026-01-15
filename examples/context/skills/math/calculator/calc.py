import sys
import argparse

def calculate(expression):
    try:
        # Security warning: eval is dangerous in production, but acceptable for this local POC
        allowed_chars = set("0123456789+-*/(). ")
        if not set(expression).issubset(allowed_chars):
             raise ValueError("Invalid characters in expression.")
        
        result = eval(expression)
        return str(result)
    except Exception as e:
        # Re-raise to be caught in main and printed to stderr
        raise e

def main():
    parser = argparse.ArgumentParser(description="Perform basic arithmetic operations.")
    parser.add_argument("expression", type=str, help="Arithmetic expression to calculate (e.g., '2 + 2')")
    
    args = parser.parse_args()
    
    try:
        result = calculate(args.expression)
        print(result) # Stdout for success
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr) # Stderr for error
        sys.exit(1)

if __name__ == "__main__":
    main()

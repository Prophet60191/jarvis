import sys
from utils import main
import logging

def run_script():
    try:
        if len(sys.argv) > 1 and sys.argv[1] != 'invalid_argument':
            print("Invalid argument. Please run the script without any arguments.")
            return
        main()

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    run_script()

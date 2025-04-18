import pygame as pg
# Import the main function 
try:
    from data.main import main
except ImportError as e: # Handle ImportError if 'data.main' is not found
    print(f"ERROR: Cannot import 'main' function from data.main: {e}")

    import sys # Import sys for handling command line arguments
    sys.exit(1) # Exit the script with an error code

# Importing tools
try:
    import data.tools
except ImportError as e:
    print(f"ERROR: Cannot import data.tools module: {e}")

    data.tools = None # setting tools to none to handle this case later.

import argparse 
import sys # Keep sys import here as well

parser = argparse.ArgumentParser(description='Pong Arguments')
parser.add_argument('-c','--clean', action='store_true',
                    help='Remove all .pyc files and __pycache__ directories')
parser.add_argument('-f' , '--fullscreen', action='store_true',
                    help='start program with fullscreen')
parser.add_argument('-d' , '--difficulty', default='medium',
                    help='where DIFFICULTY is one of the strings [hard, medium, easy], set AI difficulty, default is medium, ')
parser.add_argument('-s' , '--size', nargs=2, default=['800','600'], metavar=('WIDTH', 'HEIGHT'), # Default as strings initially
                    help='set window size to WIDTH HEIGHT, default is 800 600')


# It's better to parse arguments inside a try block too, though argparse often handles its own exits.
try:
    args = vars(parser.parse_args())
except Exception as e:
    print(f"ERROR: Failed parsing command line arguments: {e}")
    sys.exit(1)


if __name__ == '__main__':
    accepted_difficulty = ['hard', 'medium', 'easy']
    difficulty = 'medium' # Start with default
    # Use the default size from argparse as initial strings, then convert
    size_str = args['size'] # Get the size argument from argparse
 #
    size_int = [800, 600] #deault integer if the converion doesnt work

    # --- Difficulty Processing ---
    if args['difficulty'].lower() in accepted_difficulty:
        difficulty = args['difficulty'].lower()  # Set difficulty to lowercase for comparison
        print(f'Difficulty set to: {difficulty}')
    else:
        print(f"ERROR: '{args['difficulty']}' is not a valid difficulty option.")
        print(f"Choose from: {accepted_difficulty}")
        sys.exit(1) # Exit with a non-zero code to indicate an error occured

    # --- Exception handling for size processing---
    try:
        # Covert size args to integers
        width_str, height_str = size_str # Unpack the list of strings
        width = int(width_str)
        height = int(height_str)
        # Basic validation for positive dimensions
        if width > 0 and height > 0:
            size_int = [width, height]
            print(f'Window size set to: {size_int[0]}x{size_int[1]}')
        else:
            print("Warning: Window width and height must be positive. Using default size [800, 600].")
            # Keep default size_int = [800, 600] already set
    except ValueError: # Catch ValueError if int() conversion fails (a non-numeric input)
        
        print(f"ERROR: Invalid size arguments '{size_str[0]}', '{size_str[1]}'. Width and Height must be numbers.")
        print("Using default size [800, 600].")

        # Keep default size_int = [800, 600] already set
    except Exception as e: # Catch any other unexpected errors during difficulty processing

        print(f"An unexpected error occurred processing size arguments: {e}")
        print("Using default size [800, 600].")
        # Keep default size_int = [800, 600] already set

    exit_code = 0 # Assume success unless an error occurs

    # --- Clean or Run Main ---
    if args['clean']:
        if data.tools: # This check is to makes sure  the module was imported successfully
            print("Cleaning temporary files...")
            try:
                data.tools.clean_files()
                print("Cleaning complete.")
            except PermissionError:
                print("ERROR: Could not remove some files due to lack of permissions.")
                exit_code = 1 # Indicate error
            except OSError as e:
                print(f"ERROR: An OS error occurred during cleaning: {e}")
                exit_code = 1 # Indicate error
            except Exception as e:
                print(f"An unexpected error occurred during cleaning: {e}")
                exit_code = 1 # Indicate error
        else:
            print("ERROR: Cannot perform cleaning because data.tools module failed to import.")
            exit_code = 1
    else:
        # --- Run the main game loop with exception handling ---
        print("Starting game...")
        try:
            # Pass the validated integer size list to main
            main(args['fullscreen'], difficulty, size_int)
            print("Game finished normally.")
        except pg.error as e:
            # Catch Pygame-specific errors
            print(f"ERROR: A Pygame error occurred: {e}")
            exit_code = 1 # Indicate error
        except FileNotFoundError as e:
            # Example: If 'main' tries to load a file that doesn't exist
            print(f"ERROR: Required file not found: {e}")
            exit_code = 1 # Indicate error
        except ImportError as e:
             # Example: If 'main' has internal imports that fail
             print(f"ERROR: Failed to import a required module within the game: {e}")
             exit_code = 1
        except Exception as e:
            # Catch any other unexpected exceptions from the main game function
            print(f"ERROR: An unexpected error occurred during the game: {e}")

            exit_code = 1 # Indicate error
    # --- Quit Pygame if not cleaning ---
    if not args['clean']:
        print("Quitting Pygame.")
        pg.quit()

    print("Application closed.")
    sys.exit(exit_code) # Exit with 0 for success, 1 for error
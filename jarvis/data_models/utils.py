import logging
import tkinter as tk
from colorsys import hsv_to_rgb

# Set up logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

def create_color_changing_button(root):
    # Create a button that changes color when clicked
    button = tk.Button(root, bg='#ffffff')
    button.pack()

    def change_color():
        # Get the current HSV value and convert it to RGB
        hsv_value = (0.5, 0.5, 0.5)
        rgb_value = hsv_to_rgb(*hsv_value)

        # Set the button's background color to the new RGB value
        button.config(bg='#%02x%02x%02x' % tuple(int(x * 255) for x in rgb_value))

    # Bind the change_color function to the button's click event
    button.config(command=change_color)

    return button

def main():
    try:
        root = tk.Tk()
        create_color_changing_button(root)
        root.mainloop()

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()

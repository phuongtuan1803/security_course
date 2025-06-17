import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("800x400")

        # Load default icons
        self.icons = {
            "Default": "icon1.ico",
            "Alternate": "icon1.ico"
        }

        # Set initial icon
        self.set_icon("Default")

        # Load and show two images
        self.left_image_label = tk.Label(root)
        self.left_image_label.pack(side=tk.LEFT, expand=True)

        self.right_image_label = tk.Label(root)
        self.right_image_label.pack(side=tk.RIGHT, expand=True)

        self.load_images()

        # Dropdown menu to change icon
        self.icon_var = tk.StringVar(value="Default")
        icon_menu = tk.OptionMenu(root, self.icon_var, *self.icons.keys(), command=self.change_icon)
        icon_menu.pack(side=tk.BOTTOM, pady=10)

    def set_icon(self, name):
        icon_path = self.icons.get(name)
        if icon_path and os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

    def load_images(self):
        try:
            img1 = Image.open("aim_high.png").resize((300, 300))
            img2 = Image.open("aim_high.png").resize((300, 300))
            self.img1_tk = ImageTk.PhotoImage(img1)
            self.img2_tk = ImageTk.PhotoImage(img2)
            self.left_image_label.config(image=self.img1_tk)
            self.right_image_label.config(image=self.img2_tk)
        except Exception as e:
            print("Error loading images:", e)

    def change_icon(self, selection):
        self.set_icon(selection)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()

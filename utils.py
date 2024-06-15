
import tkinter as tk
from tkinter import font
from tkinter import ttk, font, simpledialog, messagebox
import random
from pymongo import MongoClient
import threading
import re
from jsonFunctions import *
from datetime import datetime
import certifi
ca = certifi.where()

def compare_norm_texts(text1, text2):
    """
    Compare two normalized texts and return True if they are equal, False otherwise.

    Parameters:
    text1 (str): The first text to compare.
    text2 (str): The second text to compare.

    Returns:
    bool: True if the normalized texts are equal, False otherwise.
    """

    def normalize_string(input_string):
        # Remove symbols using regular expression
        normalized_string = re.sub(r"[^\w\s]", "", input_string)

        # Convert to lowercase
        normalized_string = normalized_string.lower()

        # Remove spaces
        normalized_string = normalized_string.replace(" ", "")

        return normalized_string

    if text1 is None and text2 is None:
        raise ValueError("Both text1 and text2 are None")
    elif text1 is None:
        raise ValueError("text1 is None")
    elif text2 is None:
        raise ValueError("text2 is None")

    if normalize_string(text1) == normalize_string(text2):
        return True

    else:
        return False

class LabelSeparator(tk.Frame):
    def __init__(self, parent, text="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # The separator is stretched across the entire width of the frame
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.separator.grid(row=0, column=0, sticky="ew", pady=0)

        # The label is placed above the separator
        self.label = ttk.Label(self, text=text)
        self.label.grid(row=0, column=0)

        # Configure the frame to expand the column, allowing the separator to fill the space
        self.grid_columnconfigure(0, weight=1)

        # Adjust label placement using the 'sticky' parameter to center it
        # 'ns' means north-south, which centers the label vertically in the grid cell
        self.label.grid_configure(sticky="ns")

class FontSizeChanger:
    def __init__(self, position, root, font_size=12):
        self.root = root
        self.font_size = font_size
        self.exlude_widgets = []

        # "+" button to increase font size
        increase_font_button = tk.Button(
            position, text="+", command=self.increase_font_size
        )
        increase_font_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        # "-" button to decrease font size
        decrease_font_button = tk.Button(
            position, text="-", command=self.decrease_font_size
        )
        decrease_font_button.pack(side=tk.LEFT, padx=(0, 10), pady=10)

    def add_exclude_widget(self, widget):
        self.exlude_widgets.append(widget)

    def increase_font_size(self):
        """Increases the font size by 1 if it's less than 30.
        Also updates the font size and window size.
        """
        if self.font_size < 30:
            self.font_size += 1
            self.update_font_size(self.root)
            self.update_window_size(enlarge=True)

    def decrease_font_size(self):
        """Decreases the font size by 1 if it's greater than 10.
        Also updates the font size and window size.
        """
        if self.font_size > 10:
            self.font_size -= 1
            self.update_font_size(self.root)
            self.update_window_size(enlarge=False)

    def update_font_size_wrapper(self):
        """Prepares to update the whole program using a recursive function that takes the root frame and updates all the child widgets."""
        self.update_font_size(self.root)

    def update_font_size(self, widget):
        """A recursive function to update the font size of a widget and its child widgets.

        Args:
            widget (object): The tkinter object to update the font size for.
        """
        new_font = font.Font(size=self.font_size)

        try:
            if widget not in self.exlude_widgets:
                widget.configure(font=new_font)
                
        except:
            pass

        for child in widget.winfo_children():
            self.update_font_size(child)

    def update_window_size(self, enlarge):
        """Updates the window size to accommodate the text with the new font size.

        Args:
            enlarge (boolean): If True, makes the window bigger. If False, makes the window smaller.
        """
        if enlarge:
            num = 40
        else:
            num = -40

        # Get the current size of the window
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()

        # Calculate a new height, but ensure it's within the screen's limits
        screen_height = self.root.winfo_screenheight()
        new_height = min(current_height + num, screen_height)

        # Calculate a new Width, but ensure it's within the screen's limits
        screen_width = self.root.winfo_screenwidth()
        new_width = min(current_width + num * 2, screen_width)

        # Update the window size using geometry
        self.root.geometry(f"{new_width}x{new_height}")
        self.root.update()

class ProgressIndicator:
    def __init__(self, position, dialog_change_function=None):
        """
        Initializes a ProgressIndicator object.

        Args:
            position (tkinter.Tk): The position where the labels will be placed.
        """
        self.dialog_change_function = dialog_change_function
        
        # Dialog label
        self.dialog_label = tk.Label(position, text="Dialog:")
        self.dialog_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Current dialog number entry and total dialogs label
        self.entry = tk.Entry(position, font=('Arial', 12), width=5)
        self.entry.pack(side=tk.LEFT, padx=5, pady=10)
        self.entry.bind('<FocusOut>', self.update_label)
        
        self.total_dialogs_label = tk.Label(position, text="/ 0")
        self.total_dialogs_label.pack(side=tk.LEFT, padx=5, pady=10)

        # Current turn label
        self.current_turn_label = tk.Label(position, text="")
        self.current_turn_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.current_dialog_num = -1

    def update_label(self, event):
        # Get the value from the entry widget and update the label
        new_value = self.entry.get()
        if new_value.isdigit():  # Ensure the input is a number
            self.dialog_change_function(int(new_value))
        else:
            # Display an error message
            messagebox.showerror("Error", "Please enter a number")

        return "break"
    
    def get_widget(self):
        return self.entry

    def update_current_turn_dialog_labels(
        self, json_data, dialog_num, dialog_id, turn_num, count_turns
    ):
        """Updates the indicator of where the annotator is (in what dialog and what turn).

        Args:
            dialog_num (int): The dialog the annotator is on.
            turn_num (int): The turn the annotator is on.
            json_data (string): The json data.
            count_turns (int): The number of turns in the dialog.
        """
        self.current_dialog_num = dialog_num
        completed_turns_counter = 0

        for key in JsonFunctions.get_turns(json_data, dialog_id):
            if key.isdigit():
                if int(key) < turn_num:
                    completed_turns_counter += 1
                else:
                    break

        # Updates the entry widget with the current dialog number
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(dialog_num + 1))

        # Updates the total dialogs label
        self.total_dialogs_label.config(
            text=f"/ {len(json_data)}"
        )

        # Updates the turn progress label
        self.current_turn_label.config(
            text=f"Turn: {completed_turns_counter+1}/{count_turns}"
        )

class MongoData:

    class FileDialog(simpledialog.Dialog):
        """
        A dialog window for choosing a file.

        Inherits from simpledialog.Dialog class.

        Attributes:
            field1 (tk.Entry): The entry field for the username.
            field2 (tk.Entry): The entry field for the filename.
            result (tuple): A tuple containing the values entered in the entry fields.

        Methods:
            body(master): Creates the body of the dialog window.
            apply(): Applies the changes made in the dialog window.
        """

        def body(self, master):
            self.title("Choose File")

            tk.Label(master, text="username").grid(row=0)
            tk.Label(master, text="filename").grid(row=1)

            self.field1 = tk.Entry(master)
            self.field2 = tk.Entry(master)

            self.field1.grid(row=0, column=1)
            self.field2.grid(row=1, column=1)

            return self.field1

        def apply(self):
            self.result = (self.field1.get(), self.field2.get())

    def __init__(self, root, connection_string, dev_mode=False):
        """
        Initializes an instance of the MongoData class.

        Args:
            root (object): The root object of the Tkinter application.
            connection_string (str): The connection string for the MongoDB database.
        """
        self.root = root
        self.client = MongoClient(connection_string, tlsCAFile=ca)
        self.db = self.client.require_rewrite_b

        self.username = None
        self.filename = None
        self.saving_in_progress = False
        self.dev_mode = dev_mode
        
    def get_saving_status(self):
        return self.saving_in_progress
    
    def choose_file(self):
        """
        Choose a file and load its data.

        Returns:
            str: Status message indicating the result of the file loading process.
        """
        username, filename, data = None, None, None

        if self.dev_mode:
            username = "test69"
            filename = "asi-23_4"

        else:
            self.root.withdraw()
            dialog = self.FileDialog(self.root)
            username, filename = dialog.result
            print(f"filename: {filename}, username: {username}")
            self.root.deiconify()

        if "asi" in re.split(r'[ _\-]', filename):
            collection = self.db.json_annotations
            query = {"file_id": filename, "username": username}
            result = collection.find_one(query)
            if result != None:
                data = result['json_data']

        if data == None:
            query = {"file_id": filename}
            collection = self.db.json_batches
            result = collection.find_one(query)
            if result == None:
                print("File does not exist")
                self.show_error_file_not_found()
                return "done"
            else:
                data = result["json_data"]
                print(f"batch_{filename} loaded successfully. (username: {username})")

        if "asi" in re.split(r'[ _\-]', filename):
            new_data = {}
            for dialog_key, dialog_data in data.items():

                new_dialog = {"number_of_turns": 0,
                              "annotator_id": username,
                              "dialog": {}}

                for index, value in enumerate(dialog_data["dialog"]):
                    new_dialog["dialog"][str(index)] = value
                    new_dialog["number_of_turns"] += 1

                    if index > 0:
                        new_dialog["dialog"][str(index)]["requires_rewrite"] = dialog_data[str(index)]["requires_rewrite"]
                        new_dialog["dialog"][str(index)]["enough_context"] = dialog_data[str(index)]["enough_context"]

                new_data[dialog_key] = new_dialog
            data = new_data

        self.filename = filename
        self.username = username

        return self.fill_dialogs(data)

    def save_json(self, json_data, dialog_id):
        """
        Opens a thread and sends the user's progress to the MongoDB.
        """

        self.saving_in_progress = True



        # Wrap the save_json logic in a method that can be run in a thread
        thread = threading.Thread(
            target=self.save_to_mongo,
            args=(
                json_data,
                dialog_id,
            ),
        )
        thread.start()
        # Optionally, you can join the thread if you need to wait for it to finish
        # thread.join()

    def show_error_file_not_found(self):
        """
        Displays an error message indicating that the file was not found and attempts to close the program.
        """
        # Show error message
        tk.messagebox.showerror("Error", "File not found")
        # Attempt to close the program
        self.root.destroy()

    def get_username(self):
        return self.username
    
    def get_filename(self):
        return self.filename

    def save_to_mongo(self, json_data, dialog_id):
        """
        Saves the given JSON data for a specific dialog to MongoDB.

        Args:
            json_data (dict): The JSON data to be saved.
            dialog_id (str): The ID of the dialog.

        Returns:
            bool: True if the save operation was successful, False otherwise.
        """
        json_data[dialog_id]["annotator_id"] = self.username

        collection = self.db.json_annotations_dialogs
        query = {"username": self.username, "file_id": self.filename, "dialog_id": dialog_id}
        my_values = {
            "$set": {
                "username": self.username,
                "file_id": self.filename,
                "dialog_id": dialog_id,
                "dialog_data": json_data[dialog_id],
            }
        }

        update_result = collection.update_one(query, my_values, upsert=True)

        self.saving_in_progress = False  # changes this to let the program know the request is over

        if update_result.acknowledged:
            print(f"Dialog with username: {self.username} | filename: {self.filename} | dialog: {dialog_id} updated.")
            return True
        else:
            return False

    def fill_dialogs(self, json_data):
        """
        Fills the dialogs in the empty json data with all the annotations the annotator already made.
        """
        
        collection = self.db.json_annotations_dialogs
        query = {"username": self.username, "file_id": self.filename}
        results = collection.find(query)

        for result in results:
            json_data[result["dialog_id"]] = result["dialog_data"]

        return json_data

class LoadingScreen:
    def __init__(self, root):
        """
        Initializes a LoadingScreen object.

        Parameters:
        - root: The root Tkinter window.

        """
        self.root = root
        self.loading_screen = None
        self.active = False

    def show_loading_screen(self, message="Loading..."):
        """
        Displays the loading screen.

        This method creates a new Toplevel window and displays a loading screen
        with a label showing a customizable message. The loading screen prevents
        the user from interacting with the main window.

        """
        self.loading_screen = tk.Toplevel(self.root)
        self.loading_screen.title("Please wait...")
        self.loading_screen.geometry("300x150")  # Adjusted size
        self.loading_screen.transient(self.root)
        self.loading_screen.grab_set()

        # Center the loading screen relative to the main window
        self.loading_screen.geometry(
            "+%d+%d"
            % (
                self.root.winfo_rootx() + (self.root.winfo_width() - 300) // 2,
                self.root.winfo_rooty() + (self.root.winfo_height() - 150) // 2,
            )
        )

        # Make the loading screen appear on top of other windows
        self.loading_screen.attributes("-topmost", True)

        loading_label = tk.Label(self.loading_screen, text=message, wraplength=250)
        loading_label.pack(pady=20)

        self.root.update()
        self.active = True

    def close_loading_screen(self):
        """
        Closes the loading screen.

        This method destroys the loading screen window, allowing the user to
        continue interacting with the main window.

        """
        if self.loading_screen:
            self.loading_screen.destroy()
            self.loading_screen = None
        self.active = False

    def is_active(self):
        return self.active

class RequireRewriteCheckBox:
    def __init__(self, position, root, update_enough_focus_state):
        self.root = root
        self.position = position
        self.function = update_enough_focus_state

        self.requires_rewrite_frame = tk.Frame(root)
        position.add(self.requires_rewrite_frame, stretch="always", height=30)
        LabelSeparator(
            self.requires_rewrite_frame, text="Requires Rewrites Checkbox"
        ).pack(fill=tk.X)

        self.requires_rewrite_grid = tk.Frame(self.requires_rewrite_frame)
        self.requires_rewrite_grid.pack(fill=tk.BOTH, padx=10, pady=10)

        self.choice_var = tk.IntVar(value=-1)

        self.circle1 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Utterance Needs Rephrasing",
            variable=self.choice_var,
            value=1,
            command=lambda: update_enough_focus_state(),
        )
        self.circle2 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Utterance Doesn't Need Rephrasing",
            variable=self.choice_var,
            value=0,
            command=lambda: update_enough_focus_state(),
        )

        self.circle1.grid(row=0, column=0, sticky="w", padx=5, pady=0)
        self.circle2.grid(row=1, column=0, sticky="w", padx=5, pady=0)

    def on_select(self):
        """
        This method is called when an option is selected.
        It prints the value of the selected option.
        """
        print(self.choice_var.get())

    def update_entry_text(self, dialog_id, turn_num, json_data):
        """
        Updates the marked choice based on the given dialog ID, turn number, and JSON data.

        Args:
            dialog_id (int): The ID of the dialog.
            turn_num (int): The turn number.
            json_data (dict): The JSON data containing the dialog information.

        Returns:
            None
        """
        entry_text = JsonFunctions.get_require_rewrite(json_data, dialog_id, turn_num)

        if entry_text is not None and entry_text != -1:
            self.choice_var.set(int(entry_text))
        else:
            self.choice_var.set(-1)

        self.function()

    def update_json_data(self, dialog_id, turn_id, json_data):
        """
        Updates the JSON data with the new value from the requires_rewrite Entry widget.

        Args:
            dialog_id: The ID of the dialog.
            turn_id: The turn ID.
            json_data: The JSON data.

        Returns:
            dict: The modified JSON data.
        """
        new_value = self.choice_var.get()
        JsonFunctions.change_requires_rewrite(json_data, dialog_id, turn_id, new_value)
        return json_data

    def is_empty(self):
        """
        Check if the choice variable is empty.

        Returns:
            bool: True if the choice variable is empty, False otherwise.
        """
        if self.choice_var.get() == -1:
            return True
        return False

    def requires_rewrite_positive(self):
        """
        Check if the choice variable is set to 1.

        Returns:
            bool: True if the choice variable is 1, False otherwise.
        """
        if self.choice_var.get() == 1:
            return True
        return False

    def get_requires_rewrite(self):
        """
        Get the value of the choice variable.

        Returns:
            The value of the choice variable.
        """
        return self.choice_var.get()

    def set_requires_rewrite(self, value):
        """
        Sets the value of requires_rewrite.

        Args:
            value: The new value for requires_rewrite.

        Returns:
            None
        """
        self.choice_var.set(value)

    def focus_on(self):
        pass

class NeedsClarificationCheckBox:
    def __init__(self, position, root, update_enough_focus_state):
        self.root = root
        self.position = position
        self.function = update_enough_focus_state

        self.requires_rewrite_frame = tk.Frame(root)
        position.add(self.requires_rewrite_frame, stretch="always", height=30)
        LabelSeparator(
            self.requires_rewrite_frame, text="Needs Clarification Checkbox"
        ).pack(fill=tk.X)

        self.requires_rewrite_grid = tk.Frame(self.requires_rewrite_frame)
        self.requires_rewrite_grid.pack(fill=tk.BOTH, padx=10, pady=10)

        self.choice_var = tk.IntVar(value=-1)

        self.circle1 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Utterance Needs Clarification",
            variable=self.choice_var,
            value=1,
            command=lambda: update_enough_focus_state(),
        )
        self.circle2 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Utterance Doesn't Need Clarification",
            variable=self.choice_var,
            value=0,
            command=lambda: update_enough_focus_state(),
        )

        self.circle1.grid(row=0, column=0, sticky="w", padx=5, pady=0)
        self.circle2.grid(row=1, column=0, sticky="w", padx=5, pady=0)

    def on_select(self):
        """
        This method is called when an option is selected.
        It prints the value of the selected option.
        """
        print(self.choice_var.get())

    def update_entry_text(self, dialog_id, turn_num, json_data):
        """
        Updates the marked choice based on the given dialog ID, turn number, and JSON data.

        Args:
            dialog_id (int): The ID of the dialog.
            turn_num (int): The turn number.
            json_data (dict): The JSON data containing the dialog information.

        Returns:
            None
        """
        entry_text = JsonFunctions.get_require_rewrite(json_data, dialog_id, turn_num)

        if entry_text is not None and entry_text != -1:
            self.choice_var.set(int(entry_text))
        else:
            self.choice_var.set(-1)

        self.function()

    def update_json_data(self, dialog_id, turn_id, json_data):
        """
        Updates the JSON data with the new value from the requires_rewrite Entry widget.

        Args:
            dialog_id: The ID of the dialog.
            turn_id: The turn ID.
            json_data: The JSON data.

        Returns:
            dict: The modified JSON data.
        """
        new_value = self.choice_var.get()
        JsonFunctions.change_requires_rewrite(json_data, dialog_id, turn_id, new_value)
        return json_data

    def is_empty(self):
        """
        Check if the choice variable is empty.

        Returns:
            bool: True if the choice variable is empty, False otherwise.
        """
        if self.choice_var.get() == -1:
            return True
        return False

    def requires_rewrite_positive(self):
        """
        Check if the choice variable is set to 1.

        Returns:
            bool: True if the choice variable is 1, False otherwise.
        """
        if self.choice_var.get() == 1:
            return True
        return False

    def get_requires_rewrite(self):
        """
        Get the value of the choice variable.

        Returns:
            The value of the choice variable.
        """
        return self.choice_var.get()

    def set_requires_rewrite(self, value):
        """
        Sets the value of requires_rewrite.

        Args:
            value: The new value for requires_rewrite.

        Returns:
            None
        """
        self.choice_var.set(value)

    def focus_on(self):
        pass


class EnoughContext:
    def __init__(self, position, root):
        self.root = root
        self.position = position

        self.base_frame = tk.Frame(root)
        position.add(self.base_frame, stretch="always", height=30)
        LabelSeparator(self.base_frame, text="Enough Context Checkbox").pack(fill=tk.X)

        self.grid_frame = tk.Frame(self.base_frame)
        self.grid_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.choice_var = tk.IntVar(value=-1)

        self.circle1 = tk.Radiobutton(
            self.grid_frame, text="Enough Context", variable=self.choice_var, value=1
        )
        self.circle2 = tk.Radiobutton(
            self.grid_frame,
            text="Not Enough Context",
            variable=self.choice_var,
            value=0,
        )

        self.circle1.grid(row=0, column=0, sticky="w", padx=5, pady=0)
        self.circle2.grid(row=1, column=0, sticky="w", padx=5, pady=0)

    def update_entry_text(self, dialog_id, turn_num, json_data):
        """
        Updates the marked choice based on the provided dialog ID, turn number, and JSON data.

        Args:
            dialog_id (int): The ID of the dialog.
            turn_num (int): The turn number.
            json_data (dict): The JSON data containing the context.

        Returns:
            None
        """
        entry_text = JsonFunctions.get_context(json_data, dialog_id, turn_num)

        if entry_text is not None and entry_text != -1:
            self.choice_var.set(int(entry_text))
        else:
            self.choice_var.set(-1)

    def update_json_data(self, dialog_id, turn_id, json_data):
        """
        Updates the JSON data with the new value from the requires_rewrite Entry widget.

        Args:
            dialog_id: The ID of the dialog.
            turn_id: The turn ID.
            json_data: The JSON data.

        Returns:
            dict: The modified JSON data.
        """
        new_value = self.choice_var.get()
        JsonFunctions.change_context(json_data, dialog_id, turn_id, new_value)
        return json_data

    def is_empty(self):
        """
        Check if the choice variable is empty.

        Returns:
            bool: True if the choice variable is empty, False otherwise.
        """
        if self.choice_var.get() == -1:
            return True
        return False

    def context_positive(self):
        """
        Checks if the choice variable is equal to 1 and returns True if it is, otherwise returns False.
        """
        if self.choice_var.get() == 1:
            return True
        return False

    def get_context(self):
        """
        Returns the current context selected by the user.

        Returns:
            str: The selected context.
        """
        return self.choice_var.get()

    def set_context(self, value):
        """
        Sets the context value for the choice variable.

        Parameters:
        - value: The value to set as the context.

        Returns:
        None
        """
        self.choice_var.set(value)

    def focus_on(self):
        pass

class DialogFrame:
    def __init__(self, position, root):
        """
        Initializes the DialogFrame class.

        Args:
            position: The position of the frame.
            root: The root window.

        """
        self.root = root

        # Frame for Dialog widgets
        self.dialog_frame_base = tk.Frame(root, height=1)
        position.add(self.dialog_frame_base, stretch="always", height=100)
        LabelSeparator(self.dialog_frame_base, text="Dialog Text").pack(
            fill=tk.X, side=tk.TOP
        )

        # Frame to hold the Text widget and Scrollbar
        self.text_frame = tk.Frame(self.dialog_frame_base)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar for dialog text
        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # tk.Text for dialog
        self.dialog_text = tk.Text(
            self.text_frame, wrap=tk.WORD, state="disabled", yscrollcommand=self.scrollbar.set
        )
        self.dialog_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbar to work with the text widget
        self.scrollbar.config(command=self.dialog_text.yview)

    def update_dialog_text(self, new_text):
        """
        Updates the DialogFrame window with new text.

        Args:
            new_text (string): The new text to update.
        """
        # Enable the widget to modify text
        self.dialog_text.config(state="normal")

        # Update the text
        self.dialog_text.delete(1.0, tk.END)
        self.dialog_text.insert(tk.END, new_text)

        # Disable the widget to prevent user edits
        self.dialog_text.config(state="disabled")

        # Scroll to the end of the dialog text
        self.dialog_text.see(tk.END)

    def display_dialog(self, dialog_id, turn_num, json_data):
        """
        Displays a specific dialog in the DialogFrame window.

        Args:
            dialog_id (int): The ID of the dialog to access.
            turn_num (int): The turn number until which to create the text.
            json_data (string): The JSON data to use.
        """
        dialog_text_content = ""
        turns = JsonFunctions.get_turns(json_data, dialog_id, only_annotatable=False)

        for i in range(0, turn_num + 1):

            turn_data = JsonFunctions.get_turn(json_data, dialog_id, i)
                
            if i == 0:
                if len(turn_data['answer']) == 0 or turn_data['answer'] == None:
                    turn_text = f"Turn {turn_data['turn_num']}:\n"
                    turn_text += f"Intro: {turn_data['original_question']}:\n"
                    turn_text += "-" * 40 + "\n"  # Separator line
                    dialog_text_content += turn_text
                    continue

            # Format each turn
            turn_text = f"Turn {turn_data['turn_num']}:\n"
            turn_text += f"U.u: {turn_data['original_question']}\n"

            if i < turn_num:
                turn_text += f"U.s: {turn_data['answer']}\n"

            turn_text += "-" * 40 + "\n"  # Separator line

            # Append this turn's text to the dialog text content
            dialog_text_content += turn_text

        # Update the dialog text widget using the new method
        self.update_dialog_text(dialog_text_content)
        
    def scroll_up(self):
        self.dialog_text.yview_scroll(-5, "units")
    
    def scroll_down(self):
        self.dialog_text.yview_scroll(5, "units")
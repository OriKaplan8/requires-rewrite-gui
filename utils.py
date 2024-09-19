
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
import enchant
from shared_utils import compare_norm_texts
ca = certifi.where()


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

    def __init__(self, root, connection_string, login):
        """
        Initializes an instance of the MongoData class.

        Args:
            root (object): The root object of the Tkinter application.
            connection_string (str): The connection string for the MongoDB database.
        """
        self.root = root
        self.client = MongoClient(connection_string, tlsCAFile=ca)
        self.db = self.client.require_rewrite_b

        self.username = login["username"]
        self.filename = login["filename"]
        self.saving_in_progress = False
        self.needs_clarification = None
        
    def check_needs_clarification(self, json_data):
        if not json_data:
            self.needs_clarification = False
            return

        dialog_data = next(iter(json_data))
        
        if "needs_clarification" in json_data[dialog_data]["dialog"]["1"].keys():
            self.needs_clarification = True
        else:
            self.needs_clarification = False

        
    def get_saving_status(self):
        return self.saving_in_progress
    
    def load_file(self):
        """
        Choose a file and load its data.

        Returns:
            str: Status message indicating the result of the file loading process.
        """
        if self.filename is None or self.username is None:
            raise Exception("login details missing")
        
        data = None
        
        filename = self.filename
        username = self.username

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
        self.check_needs_clarification(data)
        return self.fill_dialogs(data)

    def get_needs_clarification(self):
        return self.needs_clarification
    
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
    def __init__(self, position, root, update_enough_focus_state=None):
        self.root = root
        self.position = position
        self.function = update_enough_focus_state

        self.requires_rewrite_frame = tk.Frame(root)
        position.add(self.requires_rewrite_frame, stretch="always", height=30)
        LabelSeparator(
            self.requires_rewrite_frame, text="Requires Rewrite"
        ).pack(fill=tk.X)

        self.requires_rewrite_grid = tk.Frame(self.requires_rewrite_frame)
        self.requires_rewrite_grid.pack(fill=tk.BOTH, padx=10, pady=10)

        self.choice_var = tk.IntVar(value=-1)

        self.circle1 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Requires Rewrite",
            variable=self.choice_var,
            value=1,
            command=lambda: update_enough_focus_state() if update_enough_focus_state is not None else None
        )
        self.circle2 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Doesn't Require Rewrite",
            variable=self.choice_var,
            value=0,
            command=lambda: update_enough_focus_state() if update_enough_focus_state is not None else None
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

        if self.function is not None:
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
        json_data = JsonFunctions.change_requires_rewrite(json_data, dialog_id, turn_id, new_value)
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
        if self.function is not None:
            self.function()

    def focus_on(self):
        pass

class NeedsClarificationCheckBox:
    def __init__(self, position, root):
        self.root = root
        self.position = position
        

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
            text="Needs Clarification",
            variable=self.choice_var,
            value=1,
        )
        self.circle2 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Doesn't Need Clarification",
            variable=self.choice_var,
            value=0,
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
        entry_text = JsonFunctions.get_needs_clarification(json_data, dialog_id, turn_num)

        if entry_text is not None and entry_text != -1:
            self.choice_var.set(int(entry_text))
        else:
            self.choice_var.set(-1)

        

    def update_json_data(self, dialog_id, turn_id, json_data):
        """
        Updates the JSON data with the new value from the needs_clarification Entry widget.

        Args:
            dialog_id: The ID of the dialog.
            turn_id: The turn ID.
            json_data: The JSON data.

        Returns:
            dict: The modified JSON data.
        """
        new_value = self.choice_var.get()
        json_data = JsonFunctions.change_needs_clarification(json_data, dialog_id, turn_id, new_value)
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

    def needs_clarification_positive(self):
        """
        Check if the choice variable is set to 1.

        Returns:
            bool: True if the choice variable is 1, False otherwise.
        """
        if self.choice_var.get() == 1:
            return True
        return False

    def get_needs_clarification(self):
        """
        Get the value of the choice variable.

        Returns:
            The value of the choice variable.
        """
        return self.choice_var.get()

    def set_needs_clarification(self, value):
        """
        Sets the value of needs_clarification.

        Args:
            value: The new value for needs_clarification.

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
        json_data = JsonFunctions.change_context(json_data, dialog_id, turn_id, new_value)
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
        self.dialog_text.yview_scroll(-10, "units")
    
    def scroll_down(self):
        self.dialog_text.yview_scroll(10, "units")

class Rewrites():
    def __init__(self, position, root):
        """
        Initializes the Rewrites object.

        Parameters:
        - position (tk.Position): The position object to manage the layout.
        - root (tk.Tk): The root Tkinter window.
        """
        self.rewrites = {}
        self.root = root
        self.rewrites_frame_base = tk.Frame(root)
        position.add(self.rewrites_frame_base, stretch="always", height=70)
        LabelSeparator(self.rewrites_frame_base, text="Rewrites").pack(fill=tk.X)

        # inside Frame for rewrites annotation entries
        self.rewrite_table_grid = tk.Frame(self.rewrites_frame_base)
        self.rewrite_table_grid.pack(fill=tk.BOTH, padx=10, pady=10)
        
        text = tk.Label(self.rewrite_table_grid, text="Text")
        score = tk.Label(self.rewrite_table_grid, text="Score")
        optimal = tk.Label(self.rewrite_table_grid, text="Optimal")
        
        # Place the labels in the grid
        text.grid(row=0, column=1, sticky='nsew')
        score.grid(row=0, column=2, sticky='nsew')
        optimal.grid(row=0, column=3, sticky='nsew')

        # Configure the frame columns to expand with the window size
        self.rewrite_table_grid.columnconfigure(0, weight = 1)
        self.rewrite_table_grid.columnconfigure(1, weight = 50)
        self.rewrite_table_grid.columnconfigure(2, weight = 1)
        self.rewrite_table_grid.columnconfigure(3, weight = 1)

        #label that appear if there are no rewrites
        self.no_rewrites_label = tk.Label(self.rewrite_table_grid, text="No rewrites in this turn.")
        self.no_rewrites_label.grid(column=1, row=3)
        self.no_rewrites_label.grid_remove()  # This hides the label initially
        
    def show_no_rewrites_label(self):
        self.no_rewrites_label.grid()
        
    def hide_no_rewrites_label(self):
        self.no_rewrites_label.grid_remove()
    
    def update_rewrites(self, dialog_id, turn_num, json_data):

        if not self.rewrites == {}:
            for rewrite in self.rewrites.values():
                rewrite.optimal.destroy()
                rewrite.score.destroy()
                rewrite.text.destroy()
                rewrite.rewrite_label.destroy()

        valid_rewrites_len = 0
        rewrite_row = 1
        self.rewrites = {}

        for rewrite_key, rewrite_value in JsonFunctions.get_rewrites(json_data, dialog_id, turn_num).items():
           
            
            if not {"text", "optimal", "score"}.issubset(rewrite_value.keys()):
                print(JsonFunctions.get_rewrites(json_data, dialog_id, turn_num))
                raise Exception(f"The value(s) are not in the rewrite keys: {rewrite_value.keys()}")
            
            duplicate = False
            
            for exsiting_rewrite in self.rewrites.values():
                if compare_norm_texts(exsiting_rewrite.get_text(), rewrite_value['text']):
                    exsiting_rewrite.duplicates.append(rewrite_key)
                    duplicate = True

            if duplicate == False:
                self.rewrites[rewrite_key] = (SingleRewrite(rewrite_value['text'], rewrite_value['optimal'], rewrite_value['score'], rewrite_row, self))
                
                rewrite_row += 1
                valid_rewrites_len += 1

        if valid_rewrites_len == 0:
            self.no_rewrites_label.grid()  # Show the label

        else:
            self.no_rewrites_label.grid_remove()  # Hide the label

    def update_json_data(self, dialog_id, turn_num, json_data):
        """
        Updates the JSON data with the scores and optimal values for rewrites.

        Args:
            dialog_id (str): The ID of the dialog.
            turn_num (int): The turn number.
            json_data (dict): The JSON data to be updated.

        Returns:
            dict: The updated JSON data.
        """

        def update_rewrite_field_json(rewrite_key, field, value):
            JsonFunctions.change_rewrite_field(json_data, dialog_id, turn_num, rewrite_key, field, value)

        for rewrite_key, rewrite_data in self.rewrites.items():

            score = rewrite_data.get_score()
            optimal = rewrite_data.get_optimal()

            update_rewrite_field_json(rewrite_key, 'score', score)
            update_rewrite_field_json(rewrite_key, 'optimal', optimal)

            if rewrite_data.duplicates != []:
                for duplicate in rewrite_data.duplicates:
                    update_rewrite_field_json(duplicate, 'score', score)
                    update_rewrite_field_json(duplicate, 'optimal', optimal)

        return json_data
    
    def get_max_score(self):
        """
        Returns the maximum score among all the rewrites.

        Returns:
            int: The maximum score. Returns None if any rewrite has a score of None.
        """
        max_score = 0
        for rewrite in self.rewrites.values():
            if rewrite.get_score() is None:
                return None
            if rewrite.get_score() > max_score:
                max_score = rewrite.get_score()
        return max_score
    
    def all_scores_filled(self):
        """
        Checks if all scores for the rewrites have been filled.

        Returns:
            bool: True if all scores are filled, False otherwise.
        """
        for rewrite in self.rewrites.values():
            if rewrite.get_score() == None:
                return False
        return True
    
    def clean_optimals(self):
        """
        Clears the optimal values in the rewrites.

        This method iterates through each rewrite in the `rewrites` list and clears the optimal value by deleting the existing text and inserting an empty string.

        Parameters:
            None

        Returns:
            None
        """
        for rewrite in self.rewrites.values():
            rewrite.set_optimal(None)
            
    def is_empty(self):
        """
        Checks if any rewrite in the list has a score or optimal value of None.

        Returns:
            bool: True if any rewrite has a score or optimal value of None, False otherwise.
        """
        for rewrite in self.rewrites.values():
            if rewrite.get_score() is None or rewrite.get_optimal() is None:
                return True
        return False
    
    def sync_optimals(self, score, optimal):
        """
        Synchronizes the optimal value for rewrites with a given score.

        Parameters:
        - score: The score to match against the rewrites' scores.
        - optimal: The new optimal value to set for the matching rewrites.

        Returns:
        None
        """
        for rewrite in self.rewrites.values():
            if rewrite.get_score() == score:
                rewrite.set_optimal(optimal)
                rewrite.optimal.delete(0, tk.END)
                if optimal == None:
                    optimal = ''
                rewrite.optimal.insert(0, optimal)
                
    def positive_optimal_exists(self):
        """
        Checks if an optimal rewrite exists in the list of rewrites.

        Returns:
            bool: True if an optimal rewrite exists, False otherwise.
        """
        for rewrite in self.rewrites.values():
            if rewrite.get_optimal() == 1:
                return True
        return False
    
    def handle_positive_optimal(self, score):
        """
        Sets the 'optimal' flag for rewrites with a score greater than or equal to the given score.

        Parameters:
        - score: The threshold score to compare against.

        Returns:
        None
        """
        for rewrite in self.rewrites.values():
            if rewrite.get_score() >= score:
                rewrite.set_optimal(1)
            else:
                rewrite.set_optimal(0)
    
class SingleRewrite():
   
    def __init__(self, rewrite_text, rewrite_optimal, rewrite_score, rewrite_row, rewrites_instance):
        """
        Initializes a SingleRewrite instance.

        Parameters:
            rewrite_text (str): The text content of the rewrite.
            rewrite_optimal (int or None): The optimal value for the rewrite.
            rewrite_score (int or None): The score value for the rewrite.
            
            rewrite_row (int): The row number of the rewrite in the rewrite table.
            rewrites_instance (Rewrites): The instance of the parent rewrites class.
        """
  
        self.rewrite_text = rewrite_text
        self.rewrite_instance = rewrites_instance
        self.duplicates = []

        self.text = tk.Text(rewrites_instance.rewrite_table_grid, height=1, wrap='none')
        self.score = tk.Entry(rewrites_instance.rewrite_table_grid, width=5, text=None)
        self.optimal = tk.Entry(rewrites_instance.rewrite_table_grid, width=5, text=None)

        self.init_gui(rewrites_instance.rewrite_table_grid, rewrite_text, rewrite_optimal, rewrite_score, rewrite_row)
        

    def init_gui(self, rewrite_grid, rewrite_text, rewrite_optimal, rewrite_score, rewrite_row):
        self.rewrite_label = tk.Label(rewrite_grid, text=f"Rewrite {rewrite_row}")
        self.rewrite_label.grid(column=0, row=rewrite_row)
        
        self.text.insert(tk.END, rewrite_text)
        self.text.config(state='disabled')

        self.score.insert(tk.END, rewrite_score if rewrite_score is not None else '')
        self.optimal.insert(tk.END, rewrite_optimal if rewrite_optimal is not None else '')
        
        self.text.grid(row=rewrite_row, column=1, sticky='we', padx=5, pady=5)
        self.score.grid(row=rewrite_row, column=2, sticky='we', padx=5, pady=5)
        self.optimal.grid(row=rewrite_row, column=3, sticky='we', padx=5, pady=5)

        self.optimal.bind("<KeyRelease>", self.optimal_input_handle)
        self.score.bind("<KeyRelease>", self.score_input_handle)

        self.score.bind("<FocusIn>", self.select_text)
        self.optimal.bind("<FocusIn>", self.select_text)
        
    def score_input_handle(self, event=None):
        """
        Handles the input score and performs necessary actions based on the input.

        Returns:
            bool: True if the input score is valid, False otherwise.
        """
        new_score = self.get_score()
        self.rewrite_instance.clean_optimals()
        
        if new_score == '' or new_score == None:
            self.set_score(None)
            return True
        
        elif new_score in [1,2,3,4,5,6,7,8,9]:
            return True      

        else:
            tk.messagebox.showwarning("Invalid Input", f"Allowed values are: 1-9")
            self.set_score(None)
            return False
        
    def optimal_input_handle(self, event=None):
        """
        Handles the input for the optimal value.
        
        Retrieves the text from an Entry widget and performs validation checks.
        If the input is valid, it updates the optimal value and returns True.
        If the input is invalid, it displays a warning message and returns False.
        
        Returns:
            bool: True if the input is valid and processed successfully, False otherwise.
        """
        # Retrieve text from an Entry widget
        new_optimal = self.get_optimal()
        
        if new_optimal == '' or new_optimal == None:
            self.set_optimal(None)
            return True
        
        if not self.rewrite_instance.all_scores_filled():
            tk.messagebox.showwarning("Invalid Input", f"Please fill in all scores first.")
            self.set_optimal(None)
            return False
        
        if new_optimal == 1:

            if True or (self.rewrite_instance.get_max_score() == self.get_score()):
                self.rewrite_instance.sync_optimals(self.get_score(), new_optimal)
                self.rewrite_instance.handle_positive_optimal(self.get_score())
                return True

        elif new_optimal == 0:
            self.rewrite_instance.sync_optimals(self.get_score(), new_optimal)
            return True

        else:
            self.set_optimal(None)
            tk.messagebox.showwarning("Invalid Input", f"Allowed values are: 0 or 1")
            return False
        
    def select_text(self, event=None):
        """
        Selects all the text in the widget.

        Parameters:
        - event: The event that triggered the method (optional).

        Returns:
        None
        """
        event.widget.select_range(0, tk.END)

    def get_text(self):
        """
        Retrieve the text from the text widget and return it as a string.

        Returns:
            str: The text content of the text widget.
        """
        return self.text.get(1.0, tk.END).strip()

    def get_score(self):
        """
        Retrieves the score from the input field.

        Returns:
            int or str or None: The score value entered by the user. If the score is a valid integer, it is returned as an int.
            If the score is a non-empty string, it is returned as a str. If the score is None or an empty string, None is returned.
        """
        score = self.score.get()
        if score.isdigit():
            return int(score)
        elif score != None and score != '':
            return score
        else:
            return None
    
    def set_score(self, score):
        """
        Sets the score value in the input field.

        Parameters:
            score (int or str or None): The score value to be set. If the score is None, an empty string is set.

        Returns:
            None
        """
        if score == None:
            score = ''
        self.score.delete(0, tk.END)
        self.score.insert(0, score)
        
    def get_optimal(self):
        """
        Retrieves the optimal value from the input field.

        Returns:
            int or str or None: The optimal value entered by the user. If the optimal value is a valid integer, it is returned as an int.
            If the optimal value is a non-empty string, it is returned as a str. If the optimal value is None or an empty string, None is returned.
        """
        optimal = self.optimal.get()
        if optimal.isdigit():
            return int(optimal)
        elif optimal != None and optimal != '':
            return optimal
        else:
            return None

    def set_optimal(self, optimal):
        """
        Sets the optimal value in the input field.

        Parameters:
            optimal (int or str or None): The optimal value to be set. If the optimal value is None, an empty string is set.

        Returns:
            None
        """
        if optimal == None:
            optimal = ''
        self.optimal.delete(0, tk.END)
        self.optimal.insert(0, optimal)
            
class AnnotatorRewrite():
    """
    A class representing the Annotator Rewrite component.

    Attributes:
    - position: The position object to add the Annotator Rewrite frame to.
    - root: The root Tkinter window.
    """

    
    def __init__(self, position, root):
        """
        Initializes the AnnotatorRewrite object.
        """
        self.annotator_rewrite_frame_base = tk.Frame(root)
        position.add(self.annotator_rewrite_frame_base, stretch="always", height=30)
        LabelSeparator(self.annotator_rewrite_frame_base, text="Annotator Rewrite").pack(fill=tk.X)
        
        self.annotator_rewrite_frame_grid = tk.Frame(self.annotator_rewrite_frame_base)
        self.annotator_rewrite_frame_grid.pack(fill=tk.X, padx=10, pady=10)
        
        self.annotator_rewrite_label = tk.Label(self.annotator_rewrite_frame_grid, text="Annotator Rewrite:")
        self.annotator_rewrite_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        # Single-line Text widget (height=1) with no wrapping
        self.annotator_rewrite_entry = tk.Text(self.annotator_rewrite_frame_grid, height=1, width=50, wrap="none")
        self.annotator_rewrite_entry.grid(row=1, column=1, sticky='wne', padx=5, pady=5)

        self.annotator_rewrite_frame_grid.columnconfigure(0, weight=10)
        self.annotator_rewrite_frame_grid.columnconfigure(1, weight=1000)

        # Bind events to prevent multi-line input and handle spell checking
        self.annotator_rewrite_entry.bind("<Return>", self.prevent_newline)
        self.annotator_rewrite_entry.bind("<FocusIn>", self.select_text)
        self.annotator_rewrite_entry.bind("<space>", self.check_spelling)  # Spell check on key release

        # Spell check dictionary for English
        self.english_dictionary = enchant.Dict("en_US")

        # Create a tag for misspelled words (red underline)
        self.annotator_rewrite_entry.tag_configure("misspelled", underline=True, foreground="red")

    
    def prevent_newline(self, event):
        """ Prevents the Text widget from creating a new line when Enter is pressed. """
        return 'break'  # Stops the event, preventing a new line
    
    def get_annotator_rewrite(self):
        """
        Returns the text entered in the Annotator Rewrite entry field.
        """
        text = self.annotator_rewrite_entry.get("1.0", tk.END).strip()  # Get text from tk.Text
        if text == '':
            return None
        return text
    
    def set_annotator_rewrite(self, text):
        """
        Sets the text in the Annotator Rewrite entry field.
        """
        if text is None:
            text = ''
        self.annotator_rewrite_entry.delete("1.0", tk.END)  # Clear the Text widget
        self.annotator_rewrite_entry.insert("1.0", text)  # Insert the new text
        self.check_spelling()
    
    def is_empty(self):
        """
        Checks if the Annotator Rewrite entry field is empty.
        """
        def contains_english_char(s):
            return any(c.isalpha() and c.isascii() for c in s)

        text = self.get_annotator_rewrite()
        if text is None:
            return True
        return not contains_english_char(text)
          
    def select_text(self, event=None):
        """
        Selects all the text in the Annotator Rewrite entry field.
        """
        event.widget.tag_add(tk.SEL, "1.0", tk.END)  # Select all text in tk.Text
        return 'break'  # Prevent default behavior
        
    def update_json_data(self, dialog_id, turn_num, json_data):
        """
        Updates the JSON data with the new Annotator Rewrite value.

        Parameters:
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.
        - json_data: The JSON data to update.

        Returns:
        - The updated JSON data.
        """
        new_value = self.get_annotator_rewrite()
        JsonFunctions.change_annotator_rewrite(json_data, dialog_id, turn_num, new_value)

        return json_data
     
    def update(self, dialog_id, turn_num, json_data):
        """
        Updates the Annotator Rewrite entry field with the value from the JSON data.

        Parameters:
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.
        - json_data: The JSON data.

        """

        annotator_rewrite = JsonFunctions.get_annotator_rewrite(json_data, dialog_id, turn_num)

        self.set_annotator_rewrite(annotator_rewrite)

    def check_spelling(self, event=None):
        """ Checks the spelling of words in the Text widget and underlines misspelled words in red, 
            but ignores words that start with a capital letter. """
        
        # Remove previous misspelled tags
        self.annotator_rewrite_entry.tag_remove("misspelled", "1.0", tk.END)
        
        # Get the text from the widget
        text_content = self.annotator_rewrite_entry.get("1.0", tk.END).strip()
        
        # Split the text into words
        words = text_content.split()

        start_pos = "1.0"
        for word in words:
            # Skip words that start with a capital letter
            if word[0].isupper():
                continue
            
            # Find the start position of the word
            start_pos = self.annotator_rewrite_entry.search(word, start_pos, stopindex=tk.END)
            
            if start_pos:
                end_pos = f"{start_pos} + {len(word)}c"
                
                # Check if the word is misspelled
                if not self.english_dictionary.check(word):
                    # Underline the misspelled word
                    self.annotator_rewrite_entry.tag_add("misspelled", start_pos, end_pos)
                
                # Move to the end of the current word for next search
                start_pos = end_pos

    def handle_unique(self, rewrites, original_question):
        """
        Handles the uniqueness check for the Annotator Rewrite.

        Parameters:
        - rewrites: The list of rewrites.
        - original_question: The original question.

        Returns:
        - True if the Annotator Rewrite is unique, False otherwise.
        """
        
        if self.is_empty():
            return True
        
        for rewrite in rewrites:
            if compare_norm_texts(rewrite.get_text(), self.get_annotator_rewrite()):
                self.set_annotator_rewrite(None)
                tk.messagebox.showwarning("Annotator Rewrite Identical", f"Annotator Rewrite is identical to a rewrite.")
                return False
            
        if (compare_norm_texts(self.get_annotator_rewrite(), original_question)):
            self.set_annotator_rewrite(None)
            tk.messagebox.showwarning("Annotator Rewrite Identical", f"Annotator Rewrite is identical to the original question.")
            return False
        
        return True
    

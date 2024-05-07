# %% [markdown]
# # Classes Overview
# 
# This document provides an overview of the various classes designed to manage and interact with JSON data and user interfaces for an annotation software system.
# 
# ## JsonFunctions
# 
# - **Purpose**: Provides static methods for accessing and manipulating specific fields within JSON data structures, particularly for tasks related to dialogue annotation.
# - **Key Methods**: Includes methods for retrieving and modifying annotation fields such as 'requires_rewrite' and 'annotator_rewrite', counting turns within a dialogue, and managing rewrites.
# 
# ## LabelSeparator
# 
# - **Purpose**: A utility class for creating a labeled separator within a Tkinter frame, enhancing the UI structure.
# - **Functionality**: Places a horizontal separator line with a label over it, used to demarcate different sections of the GUI clearly.
# 
# ## FontSizeChanger
# 
# - **Purpose**: Manages the font size of text within the application, providing interactive buttons to increase or decrease the displayed text size.
# - **Features**: Adjusts the entire application’s text size dynamically and updates the window size to accommodate changes, enhancing accessibility.
# 
# ## ProgressIndicator
# 
# - **Purpose**: Displays the current progress of the annotation in terms of dialogue and turn numbers.
# - **Functionality**: Updates labels to reflect the current position within the dataset, aiding annotators in tracking their progress.
# 
# ## MongoData
# 
# - **Purpose**: Handles interactions with a MongoDB database, including loading and saving JSON data.
# - **Functionality**: Includes methods to select files for annotation, save annotated data back to the database, and manage user sessions through dialogues.
# 
# ## RequireRewriteCheckBox
# 
# - **Purpose**: Provides a GUI component for annotators to indicate whether a turn requires rewriting.
# - **Features**: Uses radio buttons to capture the annotator's decision, updates JSON data based on user input, and checks if the required fields are filled before proceeding.
# 
# ## EnoughContext
# 
# - **Purpose**: Similar to RequireRewriteCheckBox but for indicating if enough context is provided in the turn.
# - **Features**: Manages user input regarding the context sufficiency of a turn and updates the corresponding JSON field.
# 
# ## DialogFrame
# 
# - **Purpose**: Displays the dialogue content to the annotator.
# - **Functionality**: Manages a text widget to display dialogue turns up to the current point of annotation, updating the display as the annotator progresses.
# 
# Each class is tailored to specific aspects of the annotation process, from user interface management to direct interactions with backend data structures. This structured approach allows for modular development and maintenance of the annotation tool.
# 

# %%
import datetime
import tkinter as tk
from tkinter import ttk, font, simpledialog, messagebox
import random
from pymongo import MongoClient
import threading
import re

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
        normalized_string = re.sub(r'[^\w\s]', '', input_string)
        
        # Convert to lowercase
        normalized_string = normalized_string.lower()
        
        # Remove spaces
        normalized_string = normalized_string.replace(' ', '')
        
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

class JsonFunctions():

    def get_require_rewrite(json_data, dialog_id, turn_num):
        """
        Retrieves the value of the 'requires_rewrite' field from the JSON data.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.

        Returns:
        - The value of the 'requires_rewrite' field.
        """
        field = ''
        if 'requires_rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'requires_rewrite'
        elif 'requires rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'requires rewrite'
        else:
            raise Exception(f"requires_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys_found = {json_data[dialog_id][str(turn_num)].keys()}")
        
        return json_data[dialog_id][str(turn_num)][field]
    
    def get_annotator_rewrite(json_data, dialog_id, turn_num):
        """
        Retrieves the value of the 'annotator_rewrite' field from the JSON data.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.

        Returns:
        - The value of the 'annotator_rewrite' field.
        """
        field = ''
        if 'annotator_rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'annotator_rewrite'
        if 'annotator rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'annotator rewrite'
        else:
            raise Exception(f"annotator_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num}")
        
        return json_data[dialog_id][str(turn_num)][field]
        
    def get_turns(json_data, dialog_id):
        turns = {}
        for key, value in json_data[dialog_id].items():
            if key.isdigit():
                turns[key] = value
        return turns

    def count_turns_in_dialog(json_data, dialog_id):
        """
        Counts the number of turns in a dialog.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.

        Returns:
        - The number of turns in the dialog.
        """
        return len(JsonFunctions.get_turns(json_data, dialog_id))
    
    def get_original_question(json_data, dialog_id, turn_num):
        """
        Retrieves the original question from the JSON data.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.

        Returns:
        - The original question.
        """
        for dialog_turn_data in json_data[dialog_id]['dialog']:
                if dialog_turn_data["turn_num"] == turn_num:
                    return dialog_turn_data["original_question"]
    
    def change_rewrite_field(json_data, dialog_id, turn_num, rewrite_key, field, new_value):
        """
        Changes the value of a field in the rewrites dictionary.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.
        - rewrite_key: The key of the rewrite.
        - field: The field to change.
        - new_value: The new value to set.

        Returns:
        - The updated JSON data.
        """
        json_data[dialog_id][str(turn_num)][rewrite_key][field] = new_value
        return json_data
    
    def change_requires_rewrite(json_data, dialog_id, turn_num, new_value):
        """
        Changes the value of the 'requires_rewrite' field in the JSON data.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.
        - new_value: The new value to set.

        Returns:
        - The updated JSON data.
        """
        field = ''
        if 'requires_rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'requires_rewrite'
        elif 'requires rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'requires rewrite'
        else:
            raise Exception(f"requires_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys found: {json_data[dialog_id][str(turn_num)].keys()}")
        
        if new_value == -1:
            new_value = None

        json_data[dialog_id][str(turn_num)][field] = new_value
        return json_data
    
    def change_annotator_rewrite(json_data, dialog_id, turn_num, new_value):
        """
        Changes the value of the 'annotator_rewrite' field in the JSON data.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.
        - new_value: The new value to set.

        Returns:
        - The updated JSON data.
        """
        field = ''
        if 'annotator_rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'annotator_rewrite'
        if 'annotator rewrite' in json_data[dialog_id][str(turn_num)].keys():
            field = 'annotator rewrite'
        else:
            raise Exception(f"annotator_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num}")
        
        json_data[dialog_id][str(turn_num)][field] = new_value
        return json_data
    
    def get_rewrites(json_data, dialog_id, turn_num):
        """
        Retrieves the rewrites from the JSON data.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.

        Returns:
        - The rewrites from the JSON data.
        """
        turn_data = json_data[dialog_id][str(turn_num)]
        rewrites = {}

        for key, value in turn_data.items():
            if isinstance(value, dict):
                rewrites[key] = value

        return dict(random.sample(list(rewrites.items()), len(rewrites)))
    
    def first_turn(json_data, dialog_id):
        """
        Retrieves the first turn in the dialog.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.

        Returns:
        - The first turn in the dialog.
        """
        return int(next(iter(JsonFunctions.get_turns(json_data, dialog_id))))
    
    def last_turn(json_data, dialog_id):
        """
        Retrieves the last turn in the dialog.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.

        Returns:
        - The last turn in the dialog.
        """
        return int(list(JsonFunctions.get_turns(json_data, dialog_id))[-1])
    
    def get_context(json_data, dialog_id, turn_num):
        return json_data[dialog_id][str(turn_num)]["enough_context"]
    
    def change_context(json_data, dialog_id, turn_num, new_value):
        if new_value == -1:
            new_value = None

        json_data[dialog_id][str(turn_num)]["enough_context"] = new_value
        return json_data
    
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

class FontSizeChanger():
    def __init__(self, position, root, font_size=12):
        self.root = root
        self.font_size = font_size

        # "+" button to increase font size
        increase_font_button = tk.Button(position, text="+", command=self.increase_font_size)
        increase_font_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        # "-" button to decrease font size
        decrease_font_button = tk.Button(position, text="-", command=self.decrease_font_size)
        decrease_font_button.pack(side=tk.LEFT, padx=(0, 10), pady=10)

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
        """Prepares to update the whole program using a recursive function that takes the root frame and updates all the child widgets.
        """
        self.update_font_size(self.root)

    def update_font_size(self, widget):
        """A recursive function to update the font size of a widget and its child widgets.

        Args:
            widget (object): The tkinter object to update the font size for.
        """
        new_font = font.Font(size=self.font_size)

        try:
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
        new_width = min(current_width + num*2, screen_width)

        # Update the window size using geometry
        self.root.geometry(f"{new_width}x{new_height}")
        self.root.update()

class ProgressIndicator():
    def __init__(self, position):
        """
        Initializes a ProgressIndicator object.

        Args:
            position (tkinter.Tk): The position where the labels will be placed.
        """
        # Current dialog and turn labels
        self.current_dialog_label = tk.Label(position, text="")
        self.current_dialog_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.current_turn_label = tk.Label(position, text="")
        self.current_turn_label.pack(side=tk.LEFT, padx=10, pady=10)
       
    def update_current_turn_dialog_labels(self, json_data, dialog_num, dialog_id, turn_num, count_turns):
        """Updates the indicator of where the annotator is (in what dialog and what turn).

        Args:
            dialog_num (int): The dialog the annotator is on.
            turn_num (int): The turn the annotator is on.
            json_data (string): The json data.
            count_turns (int): The number of turns in the dialog.
        """
        completed_turns_counter = 0
        
        for key in json_data[dialog_id].keys():
            if key.isdigit():
                if int(key) < turn_num:
                    completed_turns_counter += 1
                else:
                    break
            
        # Updates the dialog progress label
        self.current_dialog_label.config(text=f"Dialog: {dialog_num + 1}/{len(json_data)}")

        # Updates the turn progress label
        self.current_turn_label.config(text=f"Turn: {completed_turns_counter+1}/{count_turns}")

class MongoData():
    
    class FileDialog(simpledialog.Dialog):
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
            
    def __init__(self, root, connection_string):
        """
        Initializes an instance of the MongoData class.

        Args:
            root (object): The root object of the Tkinter application.
            connection_string (str): The connection string for the MongoDB database.
        """
        self.root = root
        self.client = MongoClient(connection_string)
        self.db = self.client.require_rewrite_b
        
        self.username = None
        self.filename = None
        self.saving_in_progress = False
        
        
    def get_saving_status(self):
        return self.saving_in_progress
    
    def choose_file(self, test=False):
        
        self.root.withdraw()
        dialog = self.FileDialog(self.root)
        username, filename = dialog.result
        print(f"filename: {filename}, username: {username}")
        self.root.deiconify()
        
        collection = self.db.json_annotations
        query = { "file_id": filename, "username": username}
        result = collection.find_one(query)
        data = None 
        
        if result != None:
            if test == False:
                print(f"batch_{filename} with username {username} loaded successfully")
            data = result['json_data']
            
        else:
            query = {'file_id': filename}
            collection = self.db.json_batches
            result = collection.find_one(query)
            if result == None:
                print('File does not exist')
                self.show_error_file_not_found()
                return 'done'
            else:
                data = result['json_data']
                print(f"batch_{filename} loaded successfully (firsttime)")
                
        self.filename = filename
        self.username = username
        
        return data
        
    def save_json(self, json_data, draft=False):
        """
        Opens a thread and sends the user's progress to the MongoDB.
        """
        
        self.saving_in_progress = True
        
        # Wrap the save_json logic in a method that can be run in a thread
        thread = threading.Thread(target=self.save_to_mongo, args=(json_data, draft,))
        thread.start()
        # Optionally, you can join the thread if you need to wait for it to finish
        # thread.join()

                
    def save_to_mongo(self, json_data, draft=False):
        """
        Sends the json_file (that is saved in the program memory as a string) back to MongoDB to be saved.
        """

        for dialog_id, dialog_data in json_data.items():
            dialog_data['annotator_id'] = self.username

        collection = self.db.json_annotations
        query = {'username': self.username, 'file_id': self.filename}
        my_values = {"$set": {'username': self.username, 'file_id': self.filename, 'json_data': json_data}}
        
        if draft:
            collection = self.db.json_annotations_draft
            query['timestamp'] = datetime.datetime.now()
            my_values["$set"]['timestamp'] = datetime.datetime.now()
            
        update_result = collection.update_one(query, my_values, upsert=True)
        
        counter = 0
        self.saving_in_progress = False
        
        if update_result.matched_count > 0:
            print(counter)
            counter += 1
            print(f"Document with username: {self.username} and filename: {self.filename} updated.")
        elif update_result.upserted_id is not None:
            if draft == False:
                print(f"user {self.username} saved the file {self.filename} for the first time.")
        else:
            return False

    def save_annotation_draft(self, json_data):
        self.save_json(json_data, draft=True)

    def show_error_file_not_found(self):
        # Show error message
        tk.messagebox.showerror("Error", "File not found")
        # Attempt to close the program
        self.root.destroy()

            
class LoadingScreen():
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
        self.loading_screen.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() - 300) // 2,
            self.root.winfo_rooty() + (self.root.winfo_height() - 150) // 2
        ))

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
    


class RequireRewriteCheckBox():
    def __init__(self, position, root, update_enough_focus_state):
        self.root = root
        self.position = position
        self.function = update_enough_focus_state

        self.requires_rewrite_frame = tk.Frame(root)
        position.add(self.requires_rewrite_frame, stretch="always", height=30)
        LabelSeparator(self.requires_rewrite_frame, text="Requires Rewrites Checkbox").pack(fill=tk.X)
        
        self.requires_rewrite_grid = tk.Frame(self.requires_rewrite_frame)
        self.requires_rewrite_grid.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.choice_var = tk.IntVar(value=-1)
        
        self.circle1 = tk.Radiobutton(self.requires_rewrite_grid, text="Question Requires Rewrite", variable=self.choice_var, value=1, command=lambda: update_enough_focus_state())
        self.circle2 = tk.Radiobutton(self.requires_rewrite_grid, text="Question Does Not Require Rewrite", variable=self.choice_var, value=0, command=lambda: update_enough_focus_state())
        
        self.circle1.grid(row=0, column=0, sticky='w', padx=5, pady=0)
        self.circle2.grid(row=1, column=0, sticky='w', padx=5, pady=0)
        
    def on_select(self):
        print(self.choice_var.get())
        
    def update_entry_text(self, dialog_id, turn_num, json_data):
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
        if self.choice_var.get() == -1:
            return True
        return False
    
    def requires_rewrite_positive(self):
        if self.choice_var.get() == 1:
            return True
        return False
    
    def get_requires_rewrite(self):
        return self.choice_var.get()
    
    def set_requires_rewrite(self, value):
        self.choice_var.set(value)
        
    def focus_on(self):
        pass

class EnoughContext():
    def __init__(self, position, root):
        self.root = root
        self.position = position
        
        self.base_frame = tk.Frame(root)
        position.add(self.base_frame, stretch="always", height=30)
        LabelSeparator(self.base_frame, text="Enough Context Checkbox").pack(fill=tk.X)
        
        self.grid_frame = tk.Frame(self.base_frame)
        self.grid_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.choice_var = tk.IntVar(value=-1)
        
        self.circle1 = tk.Radiobutton(self.grid_frame, text="Enough Context", variable=self.choice_var, value=1)
        self.circle2 = tk.Radiobutton(self.grid_frame, text="Not Enough Context", variable=self.choice_var, value=0)
        
        self.circle1.grid(row=0, column=0, sticky='w', padx=5, pady=0)
        self.circle2.grid(row=1, column=0, sticky='w', padx=5, pady=0)
        
        
    def update_entry_text(self, dialog_id, turn_num, json_data):
        
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
        if self.choice_var.get() == -1:
            return True
        return False
    
    def context_positive(self):
        if self.choice_var.get() == 1:
            return True
        return False
    
    def get_context(self):
        return self.choice_var.get()
    
    def set_context(self, value):
        self.choice_var.set(value)
        
    def focus_on(self):
        pass

class DialogFrame():
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
        LabelSeparator(self.dialog_frame_base, text="Dialog Text").pack(fill=tk.X, side=tk.TOP)

        # tk.Text for dialog
        self.dialog_text = tk.Text(self.dialog_frame_base, wrap=tk.WORD, state='disabled')
        self.dialog_text.pack(fill=tk.BOTH, padx=10, pady=10)  

    def update_dialog_text(self, new_text):
        """
        Updates the DialogFrame window with new text.

        Args:
            new_text (string): The new text to update.
        """
        # Enable the widget to modify text
        self.dialog_text.config(state='normal')

        # Update the text
        self.dialog_text.delete(1.0, tk.END)
        self.dialog_text.insert(tk.END, new_text)

        # Disable the widget to prevent user edits
        self.dialog_text.config(state='disabled')

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
        
        turn_num_real = turn_num
          
        for dialog in json_data[dialog_id]['dialog']:
            if dialog['turn_num'] <= turn_num_real:
                # Format each turn
                turn_text = f"Turn {dialog['turn_num']}:\n"
                turn_text += f"Q: {dialog['original_question']}\n"
                if dialog['turn_num'] != turn_num_real:
                    turn_text += f"A: {dialog['answer']}\n"
                turn_text += "-" * 40 + "\n"  # Separator line

                # Append this turn's text to the dialog text content
                dialog_text_content += turn_text 

        # Update the dialog text widget using the new method
        self.update_dialog_text(dialog_text_content)

# %% [markdown]
# # Annotation Application Class Description
# 
# This class, `AnnotationApp`, sets up a GUI for an annotation tool specifically tailored for rewriting operations. The tool is designed to facilitate the annotation process, allowing users to review, edit, and annotate dialog data loaded from a MongoDB database.
# 
# ## Class Initialization
# 
# - **Window Settings**: Initializes the main window with a specified title and minimum size.
# - **Top Panel Frame**: A frame at the top of the window that holds navigation and control buttons.
# - **Main PanedWindow**: A vertically oriented pane that houses the main content of the application.
# - **Navigation Buttons**: Includes buttons to navigate between turns and dialogs within the loaded JSON data.
# - **Disabling Copy-Paste**: Option to disable copy and paste operations within the application to prevent data mishandling.
# - **JSON Data Loading**: Connects to a MongoDB database to retrieve JSON data, which acts as the template for annotations.
# - **Dynamic Content**: Components such as progress indicators, dialog frames, and options for modifying text size and checking required fields.
# 
# ## Key Methods
# 
# ### `find_next_empty_turn`
# Searches through the loaded JSON data to locate the next unannotated turn, setting the application to display this turn.
# 
# ### `are_all_fields_filled`
# Checks if all required fields in the current turn are filled before allowing navigation to another turn.
# 
# ### `update_json`
# Updates the JSON data in the backend database after modifications in the GUI.
# 
# ### `get_dialog_id`
# Retrieves the ID of the current dialog being annotated.
# 
# ### `init_turn`
# Initializes the GUI components with data from the current turn, updating visual elements to reflect the current state of the annotation.
# 
# ### `prev_turn` and `next_turn`
# Methods to navigate to the previous or next turn within the dialog. These handle data saving and validation checks to ensure data integrity.
# 
# ### `prev_dialog` and `next_dialog`
# Methods to navigate between dialogs. They perform similar validation and update operations as the turn navigation methods.
# 
# ### `are_all_turns_filled`
# Checks if all turns within the current dialog have been annotated before moving to the next dialog.
# 
# ### `update_enough_focus_state`
# Updates the state of the enough context options based on the user's selection in the requires rewrite option.
# 
# ## Exception Handling
# 
# - **JSON Data Validation**: Ensures that the application does not start with null or empty JSON data to prevent errors during operation.
# 
# This class is an essential part of the annotation software, enabling efficient and organized annotation of dialog data for projects requiring text rewriting or corrections.
# 

# %%

class AnnotationApp:

    def __init__(self, root, ):
        
        # Main windows settings
        self.root = root
        self.root.title("OneAI ReWrite Annotation Software - Only Requires Rewrite")  

        # Set the minimum size of the window
        root.minsize(1000, 800)
        self.root.update()
        self.fields_check = True
        self.disable_copy = True
                       
        # Create a Top Panel Frame for options
        top_panel_frame = tk.Frame(root)
        top_panel_frame.pack(side=tk.TOP, fill=tk.X)
        version_label = tk.Label(top_panel_frame, text="Version 2.0")
        version_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Create Main PanedWindow
        main_pane = tk.PanedWindow(root, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
      
        # "<" (Previous) and ">" (Next) buttons next to each other
        prev_button = tk.Button(top_panel_frame, text="<", command=self.prev_turn)
        prev_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        next_button = tk.Button(top_panel_frame, text=">", command=self.next_turn)
        next_button.pack(side=tk.LEFT)
        
        # "<<" (Previous Dialog) and ">>" (Next Dialog) buttons
        prev_dialog_button = tk.Button(top_panel_frame, text="<<", command=self.prev_dialog)
        prev_dialog_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        next_dialog_button = tk.Button(top_panel_frame, text=">>", command=self.next_dialog)
        next_dialog_button.pack(side=tk.LEFT)
        
        # Disable Copy Paste 
        if self.disable_copy == True:
            root.event_delete('<<Paste>>', '<Control-v>')
            root.event_delete('<<Copy>>', '<Control-c>')

        # Save Button at the top
        self.save_button = tk.Button(top_panel_frame, text="Save", command=self.save_json)
        self.save_button.pack(side=tk.RIGHT, pady=10, padx=(0, 10))

        # Next Button at the bottom
        self.bottom_next_button = tk.Button(root, text="Next Turn", command=self.next_turn)
        self.bottom_next_button.pack(side=tk.BOTTOM, pady=10)
        self.root.bind("<Return>", self.next_turn)
        
        # Override the window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Load JSON data
        connection_string = "mongodb+srv://ori:CqxF0bLlZoX2OQoD@cluster0.agjlk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.mongo = MongoData(self.root, connection_string)
        self.json_data = self.mongo.choose_file()
        
        self.progress = ProgressIndicator(top_panel_frame)
        self.dialog_frame = DialogFrame(main_pane, root)
        self.font = FontSizeChanger(top_panel_frame, root)
        self.require_rewrite = RequireRewriteCheckBox(main_pane, root, self.update_enough_focus_state)
        self.enough_context = EnoughContext(main_pane, root)
        self.LoadingScreen = LoadingScreen(root)

       
        
        if(self.json_data == None or self.json_data == ''):
            raise Exception(f"The json files is Null.\n JSON={self.json_data}")

        # Load JSON and display data
        self.save_counter = 15
        self.current_dialog_num = 0
        self.current_turn_num = 0
        self.find_next_empty_turn()
        
        self.init_turn()
        
    def on_closing(self):
        """This function is called when the user tries to close the program. It checks if the user has saved the file, and if not, it asks the user if they want to save it."""
        if self.mongo.get_saving_status() == True:
            if self.LoadingScreen.is_active() == False:
                self.LoadingScreen.show_loading_screen(message="Program will close automatically after saving is done. Please wait.")
            self.root.after(1000, self.on_closing)  # Check again in 1 second
        else:
            self.mongo.client.close()
            self.root.destroy()
    
    def find_next_empty_turn(self):
        """ goes through the json_file and finds the next turn which is not filled already, then sets the program to show the turn"""
        for dialog_index, dialog_id in enumerate(self.json_data):
            dialog_data = self.json_data[dialog_id]
            for key in dialog_data.keys():
                if key.isdigit():
                    if JsonFunctions.get_require_rewrite(self.json_data, dialog_id, key) == None or JsonFunctions.get_context(self.json_data, dialog_id, key) == None:
                        self.current_dialog_num = dialog_index
                        self.current_turn_num = int(key)
                        return
                
        self.current_dialog_num = self.count_dialogs_in_batch()-1
        self.current_turn_num = self.count_turns_in_dialog()-1
    
    def are_all_fields_filled(self):
        """check if the turn the annotator is currently on is saved comletly, used before moving to the next turn

        Returns:
            boolean: True if everything is filled, False if not.
        """
        missing_fields = []

        if self.require_rewrite.is_empty():
            missing_fields.append('Requires-Rewrite')

        if self.enough_context.is_empty():
            missing_fields.append('Enough-Context')
       
        if missing_fields and self.fields_check:
            tk.messagebox.showwarning("Warning", "The following fields are missing: " + ", ".join(missing_fields) + ". Please fill them in before proceeding.")
            return False
        
        return True
    
    def save_json(self):
        self.LoadingScreen.show_loading_screen(message="Saving your progress...")
        self.update_json()
        finished = False
        if self.mongo.save_to_mongo(self.json_data) == False:
            tk.messagebox.showerror("Error", "An error occurred while saving the file. Do not close the app, and contact Ori.")
        else:
            finished = True

        if self.save_counter % 20 == 0:
            self.mongo.save_annotation_draft(self.json_data)
            
        self.LoadingScreen.close_loading_screen()
        if finished == True:
            tk.messagebox.showinfo("Success", "The file was saved successfully.")
        

    def update_json(self, prev=False):
        """updates the json_file inside the Data class (MongoDB or JsonHandler), to be saved later

        Raises:
            MemoryError: Raises when using online mode, and the annotation was not saved correctly in MongoDB

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        self.json_data = self.require_rewrite.update_json_data(self.get_dialog_id(), self.current_turn_num, self.json_data)
        self.json_data = self.enough_context.update_json_data(self.get_dialog_id(), self.current_turn_num, self.json_data)
        
        return True
        
    def get_dialog_id(self):
        """simply gets the string of the dialog_id using the current num of the dialog in the batch file

        Returns:
            string: the dialog_id
        """
        return list(self.json_data.keys())[self.current_dialog_num]

    def init_turn(self):
        """This is an important function which initializes and updates the GUI for each turn.
        
        It performs the following tasks:
        1. Updates the current turn dialog labels.
        2. Displays the dialog frame.
        3. Updates the entry text for rewriting.
        4. Updates the rewrites.
        5. Updates the annotator rewrite.
        6. Updates the font size.
        7. Sets focus on the requires_rewrite_entry.
        8. Prints the progress string.
        """
        progress_string = f"Turn={self.current_turn_num+1} | Dialog={self.current_dialog_num+1}"
        print(progress_string)
        self.save_counter += 1
        self.progress.update_current_turn_dialog_labels(self.json_data, self.current_dialog_num, self.get_dialog_id(), self.current_turn_num, JsonFunctions.count_turns_in_dialog(self.json_data, self.get_dialog_id()))
        self.dialog_frame.display_dialog(self.get_dialog_id(), self.current_turn_num, self.json_data)
        self.require_rewrite.update_entry_text(self.get_dialog_id(), self.current_turn_num, self.json_data)  
        self.enough_context.update_entry_text(self.get_dialog_id(), self.current_turn_num, self.json_data)  
        self.font.update_font_size_wrapper()
        self.require_rewrite.focus_on()
        
    def get_first_turn_index(self):

        return JsonFunctions.first_turn(self.json_data, self.get_dialog_id())

    def get_original_question(self):
            """
            Retrieves the original question from the dialog data based on the current turn number.

            Returns:
                str: The original question from the dialog data.
            """
            return JsonFunctions.get_original_question(self.json_data, self.get_dialog_id(), self.current_turn_num)
        
    def count_turns_in_dialog(self):
        """count the number of turn in the dialog

        Returns:
            int: number of turns in dialog
        """
        return JsonFunctions.count_turns_in_dialog(self.json_data, self.get_dialog_id())
    
    def count_dialogs_in_batch(self):
        """count the number of dialogs in the batch file

        Returns:
            int: number of dialogs in batch
        """
        return len(self.json_data)
     
    def prev_turn(self):
        """goes to the previous turn in the dialog
            if there are no more turns, go to the prev dialog,
            if there are no more dialogs and using mongo, goes to prev batch (if offline need to manually change target.json)

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        
        if not self.update_json(prev=True):
            return False
        
        if self.current_turn_num > JsonFunctions.first_turn(self.json_data, self.get_dialog_id()):
            self.current_turn_num -= 1
            self.init_turn()
            
        else:
            self.prev_dialog()
            
        return True
    
    def next_turn(self, event = None):
        """goes to the previous turn in the dialog
            if there are no more turns, go to the next dialog,
            if there are no more dialogs and using mongo, goes to next batch (if offline need to manually change target.json)

        Returns:
            boolean: Return True if opertion was successful, False if not
        """

        if not self.are_all_fields_filled():
            return False
        
        elif not self.update_json():
            return False
        
        
        self.mongo.save_json(json_data=self.json_data)
        
        if self.current_turn_num < JsonFunctions.last_turn(self.json_data, self.get_dialog_id()):
            self.current_turn_num += 1
            self.init_turn()
            
        else:
            self.next_dialog()
        
        return True

    def prev_dialog(self):
        """used in the prev dialog button to go to prev dialog
        """
       
        if self.current_dialog_num > 0:
                if not self.require_rewrite.is_empty():
                        self.update_json()
                        
                self.current_dialog_num -= 1
                self.current_turn_num = JsonFunctions.last_turn(self.json_data, self.get_dialog_id())
                self.init_turn()
                self.font.update_font_size_wrapper()

        else:
            tk.messagebox.showwarning("Warning", "This is the first dialog")

    def next_dialog(self):
        """used in the next dialog button to go to prev dialog
        """
       
        if self.current_dialog_num < len(self.json_data) - 1:
            if self.fields_check:
                if self.are_all_turns_filled():
                    if not self.require_rewrite.is_empty():
                        self.update_json()
                    self.current_dialog_num += 1
                    self.current_turn_num = self.get_first_turn_index()
                    self.init_turn()
                    
                else:
                    tk.messagebox.showwarning("Warning", "Not all turns in this dialog are filled")
            else:
                self.update_json()
                self.current_dialog_num += 1
                self.current_turn_num = self.get_first_turn_index()
                self.init_turn()
                    
        else:
            tk.messagebox.showinfo(title='Finished Annotating!', message='No More Annotations', icon='info')
                                          
    def are_all_turns_filled(self):
        """when going to the next dialog using the button, checks if all the turns in the dialog are filled


        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        turns = JsonFunctions.get_turns(self.json_data, self.get_dialog_id())
        for turn in turns.values():
            if JsonFunctions.get_require_rewrite(self.json_data, self.get_dialog_id(), self.current_turn_num) is None: return False
        return True
    
    def update_enough_focus_state(self):
        if self.require_rewrite.choice_var.get() == 0:
            self.enough_context.choice_var.set(1)
            self.enough_context.circle1.config(state='disabled')
            self.enough_context.circle2.config(state='disabled')
        else:
            self.enough_context.circle1.config(state='normal')
            self.enough_context.circle2.config(state='normal')
            self.enough_context.choice_var.set(-1)



# %%
def main():
    root = tk.Tk()
    app = AnnotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()



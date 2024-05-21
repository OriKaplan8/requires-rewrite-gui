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


class JsonFunctions:

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
        field = ""
        if "requires_rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "requires_rewrite"
        elif "requires rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "requires rewrite"
        else:
            raise Exception(
                f"requires_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys_found = {json_data[dialog_id][str(turn_num)].keys()}"
            )

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
        field = ""
        if "annotator_rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "annotator_rewrite"
        if "annotator rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "annotator rewrite"
        else:
            raise Exception(
                f"annotator_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num}"
            )

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
        for dialog_turn_data in json_data[dialog_id]["dialog"]:
            if dialog_turn_data["turn_num"] == turn_num:
                return dialog_turn_data["original_question"]

    def change_rewrite_field(
        json_data, dialog_id, turn_num, rewrite_key, field, new_value
    ):
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
        field = ""
        if "requires_rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "requires_rewrite"
        elif "requires rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "requires rewrite"
        else:
            raise Exception(
                f"requires_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys found: {json_data[dialog_id][str(turn_num)].keys()}"
            )

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
        field = ""
        if "annotator_rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "annotator_rewrite"
        if "annotator rewrite" in json_data[dialog_id][str(turn_num)].keys():
            field = "annotator rewrite"
        else:
            raise Exception(
                f"annotator_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num}"
            )

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


class FontSizeChanger:
    def __init__(self, position, root, font_size=12):
        self.root = root
        self.font_size = font_size

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
        completed_turns_counter = 0

        for key in json_data[dialog_id].keys():
            if key.isdigit():
                if int(key) < turn_num:
                    completed_turns_counter += 1
                else:
                    break

        # Updates the dialog progress label
        self.current_dialog_label.config(
            text=f"Dialog: {dialog_num + 1}/{len(json_data)}"
        )

        # Updates the turn progress label
        self.current_turn_label.config(
            text=f"Turn: {completed_turns_counter+1}/{count_turns}"
        )


class MongoData:

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
        query = {"file_id": filename, "username": username}
        result = collection.find_one(query)
        data = None

        if result != None:
            if test == False:
                print(f"batch_{filename} with username {username} loaded successfully")
            data = result["json_data"]

        else:
            query = {"file_id": filename}
            collection = self.db.json_batches
            result = collection.find_one(query)
            if result == None:
                print("File does not exist")
                self.show_error_file_not_found()
                return "done"
            else:
                data = result["json_data"]
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
        thread = threading.Thread(
            target=self.save_to_mongo,
            args=(
                json_data,
                draft,
            ),
        )
        thread.start()
        # Optionally, you can join the thread if you need to wait for it to finish
        # thread.join()

    def save_to_mongo(self, json_data, draft=False):
        """
        Sends the json_file (that is saved in the program memory as a string) back to MongoDB to be saved.
        """

        for dialog_id, dialog_data in json_data.items():
            dialog_data["annotator_id"] = self.username

        collection = self.db.json_annotations
        query = {"username": self.username, "file_id": self.filename}
        my_values = {
            "$set": {
                "username": self.username,
                "file_id": self.filename,
                "json_data": json_data,
            }
        }

        if draft:
            collection = self.db.json_annotations_draft
            query["timestamp"] = datetime.datetime.now()
            my_values["$set"]["timestamp"] = datetime.datetime.now()

        update_result = collection.update_one(query, my_values, upsert=True)

        counter = 0
        self.saving_in_progress = False

        if update_result.matched_count > 0:
            print(counter)
            counter += 1
            print(
                f"Document with username: {self.username} and filename: {self.filename} updated."
            )
        elif update_result.upserted_id is not None:
            if draft == False:
                print(
                    f"user {self.username} saved the file {self.filename} for the first time."
                )
        else:
            return False

    def save_annotation_draft(self, json_data):
        self.save_json(json_data, draft=True)

    def show_error_file_not_found(self):
        # Show error message
        tk.messagebox.showerror("Error", "File not found")
        # Attempt to close the program
        self.root.destroy()


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
            text="Question Requires Rewrite",
            variable=self.choice_var,
            value=1,
            command=lambda: update_enough_focus_state(),
        )
        self.circle2 = tk.Radiobutton(
            self.requires_rewrite_grid,
            text="Question Does Not Require Rewrite",
            variable=self.choice_var,
            value=0,
            command=lambda: update_enough_focus_state(),
        )

        self.circle1.grid(row=0, column=0, sticky="w", padx=5, pady=0)
        self.circle2.grid(row=1, column=0, sticky="w", padx=5, pady=0)

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

        # tk.Text for dialog
        self.dialog_text = tk.Text(
            self.dialog_frame_base, wrap=tk.WORD, state="disabled"
        )
        self.dialog_text.pack(fill=tk.BOTH, padx=10, pady=10)

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

        turn_num_real = turn_num

        for dialog in json_data[dialog_id]["dialog"]:
            if dialog["turn_num"] <= turn_num_real:
                # Format each turn
                turn_text = f"Turn {dialog['turn_num']}:\n"
                turn_text += f"Q: {dialog['original_question']}\n"
                if dialog["turn_num"] != turn_num_real:
                    turn_text += f"A: {dialog['answer']}\n"
                turn_text += "-" * 40 + "\n"  # Separator line

                # Append this turn's text to the dialog text content
                dialog_text_content += turn_text

        # Update the dialog text widget using the new method
        self.update_dialog_text(dialog_text_content)

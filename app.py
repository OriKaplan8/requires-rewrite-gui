from utils import (
    JsonFunctions,
    ProgressIndicator,
    FontSizeChanger,
    EnoughContext,
    RequireRewriteCheckBox,
    LoadingScreen,
    DialogFrame,
    MongoData,
)
import tkinter as tk
from tkinter import font

class AnnotationApp:

    def __init__(
        self,
        root,
    ):

        # Main windows settings
        self.root = root
        self.root.title("OneAI ReWrite Annotation Software - Only Requires Rewrite")

        # Set the minimum size of the window
        root.minsize(1200, 800)
        self.root.update()
        self.fields_check = True

        self.save_before_exit = False
        self.dev_mode = False

        # Create a Top Panel Frame for options
        top_panel_frame = tk.Frame(root)
        top_panel_frame.pack(side=tk.TOP, fill=tk.X) 
        version_label = tk.Label(top_panel_frame, text="Version 3.0")
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
        prev_dialog_button = tk.Button(
            top_panel_frame, text="<<", command=self.prev_dialog
        )
        prev_dialog_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        next_dialog_button = tk.Button(
            top_panel_frame, text=">>", command=self.next_dialog
        )
        next_dialog_button.pack(side=tk.LEFT)

        self.root.bind('<KeyPress>', self.quick_annotation)

        # Save Button at the top
        self.save_button = tk.Button(
            top_panel_frame, text="Save", command=self.save_json
        )
        self.save_button.pack(side=tk.RIGHT, pady=10, padx=(0, 10))

        # Create status bar frame with a darker background color
        self.status_bar = tk.Frame(self.root, bd=1, relief=tk.SUNKEN, height=25, bg="#ebebeb")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.dialog_text = tk.Text(self.status_bar, wrap=tk.WORD, height=1, bg="#ebebeb", bd=0)
        self.dialog_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dialog_text.config(state=tk.DISABLED)
        
        # Create a label for the status bar
   
        self.dialog_label = tk.Label(self.status_bar, text="", bg="#ebebeb")
        self.dialog_label.pack(side=tk.LEFT, padx=10)
        

        # Next Button at the bottom
        self.bottom_next_button = tk.Button(
            root, text="Next Turn", command=self.next_turn
        )
        self.bottom_next_button.pack(side=tk.BOTTOM, pady=10)
        self.root.bind("<Return>", self.next_turn)

        # Override the window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Load JSON data
        connection_string = "mongodb+srv://ori:CqxF0bLlZoX2OQoD@cluster0.agjlk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.mongo = MongoData(self.root, connection_string, self.dev_mode)
        self.json_data = self.mongo.choose_file()

        self.progress = ProgressIndicator(top_panel_frame, dialog_change_function=self.change_dialog)
        self.dialog_frame = DialogFrame(main_pane, root)
        self.font = FontSizeChanger(top_panel_frame, root)
        self.font.add_exclude_widget(self.dialog_label)
        self.require_rewrite = RequireRewriteCheckBox(
            main_pane, root, self.update_enough_focus_state
        )
        self.enough_context = EnoughContext(main_pane, root)
        self.LoadingScreen = LoadingScreen(root)

        if self.json_data == None or self.json_data == "":
            raise Exception(f"The json files is Null.\n JSON={self.json_data}")

        # Load JSON and display data
        self.save_counter = 15
        self.max_dialog_num = 0
        self.current_dialog_num = 0
        self.current_turn_num = 0
        self.find_next_empty_turn()

        self.init_turn()

    def change_dialog(self, dialog_num):
        """
        Change the current dialog to the specified dialog number.

        Args:
            dialog_num (int): The dialog number to change to.

        Returns:
            bool: True if the dialog was successfully changed, False otherwise.
        """
        dialog_num -= 1
        if int(dialog_num) > len(self.json_data):
            tk.messagebox.showerror(
                "Error",
                f"Dialog {dialog_num + 1} does not exist in the file. Please enter a valid dialog number.",
            )
            self.update_progress_bar()
            return False
        
        elif dialog_num > self.max_dialog_num:
            tk.messagebox.showerror(
                "Error",
                f"Dialog {dialog_num + 1} is not available yet. Please annotate the previous dialogs first.",
            )
            self.update_progress_bar()
            return False
        
        elif dialog_num < 0:
            tk.messagebox.showerror(
                "Error",
                f"Dialog {dialog_num + 1} does not exist in the file. Please enter a valid dialog number.",
            )
            self.update_progress_bar()
            return False

        self.current_dialog_num = dialog_num
        self.current_turn_num = self.get_first_turn_index()
        self.init_turn()

    def update_status_bar(self, dialog_id):
        """
        Update the status bar with the provided dialog_id.

        Parameters:
        - dialog_id (str): The ID of the dialog.

        Returns:
        - None
        """
        myfont = font.Font(family="Helvetica", size=9, weight="bold")
        
        # Enable the text widget to update its content
        self.dialog_text.config(state=tk.NORMAL)
        
        # Clear the previous content
        self.dialog_text.delete(1.0, tk.END)
        
        # Insert the new content
        status_text = (
            f"Dialog: {dialog_id} | Dialog Index: {self.current_dialog_num} | Turn Index: {self.current_turn_num} | "
            f"Total Turns: {self.count_turns_in_dialog()} | Total Dialogs: {self.count_dialogs_in_batch()} | "
            f"Next Unfilled Dialog Index: {self.max_dialog_num} | username: {self.mongo.get_username()} | "
            f"file: {self.mongo.get_filename()}"
        )
        self.dialog_text.insert(tk.END, status_text)
        
        # Apply the font
        self.dialog_text.tag_configure("font", font=myfont)
        self.dialog_text.tag_add("font", 1.0, tk.END)
        
        # Disable the text widget to make it read-only
        self.dialog_text.config(state=tk.DISABLED)

    def update_progress_bar(self):
        """
        Updates the progress bar with the current turn dialog labels.

        Parameters:
        - json_data (dict): The JSON data containing the dialog information.
        - current_dialog_num (int): The current dialog number.
        - dialog_id (str): The ID of the dialog.
        - current_turn_num (int): The current turn number.
        - total_turns (int): The total number of turns in the dialog.

        Returns:
        None
        """
        self.progress.update_current_turn_dialog_labels(
            self.json_data,
            self.current_dialog_num,
            self.get_dialog_id(),
            self.current_turn_num,
            JsonFunctions.count_turns_in_dialog(self.json_data, self.get_dialog_id()),
        )

    def quick_annotation(self, event):
        """
        Handles quick annotation based on the key pressed.

        Args:
            event (Event): The event object containing information about the key press.

        Returns:
            None
        """
        if event.keycode == 65:  # Keycode for 'z' on many keyboards
            self.require_rewrite.choice_var.set(1)
            self.enough_context.choice_var.set(1)
            self.next_turn()

        elif event.keycode == 83:  # Keycode for 'x' on many keyboards
            self.require_rewrite.choice_var.set(0)
            self.enough_context.choice_var.set(1)
            self.next_turn()

        elif event.keycode == 68:  # Keycode for 'c' on many keyboards
            self.require_rewrite.choice_var.set(1)
            self.enough_context.choice_var.set(0)
            self.next_turn()

        elif event.keycode == 37:
            self.prev_turn()

        elif event.keycode == 39:
            self.next_turn()

    def on_closing(self):
        """This function is called when the user tries to close the program. It checks if the user has saved the file, and if not, it asks the user if they want to save it."""
        if self.save_before_exit == False:
            return self.root.destroy()
        
        if self.mongo.get_saving_status() == True:
            if self.LoadingScreen.is_active() == False:
                self.LoadingScreen.show_loading_screen(
                    message="Program will close automatically after saving is done. Please wait."
                )
            self.root.after(1000, self.on_closing)  # Check again in 1 second
        else:
            self.mongo.client.close()
            self.root.destroy()

    def find_next_empty_turn(self):
        """goes through the json_file and finds the next turn which is not filled already, then sets the program to show the turn"""
        for dialog_index, dialog_id in enumerate(self.json_data):
            dialog_data = self.json_data[dialog_id]
            turns = JsonFunctions.get_turns(self.json_data, dialog_id)

            for key in turns.keys():
                if key.isdigit():
                    if (
                        JsonFunctions.get_require_rewrite(
                            self.json_data, dialog_id, key
                        )
                        == None
                        or JsonFunctions.get_context(self.json_data, dialog_id, key)
                        == None
                    ):
                        self.current_dialog_num = dialog_index 
                        self.max_dialog_num = dialog_index 
                        self.current_turn_num = int(key)
                        return

        self.current_dialog_num = self.count_dialogs_in_batch() - 1
        self.current_turn_num = self.count_turns_in_dialog() - 1
        self.max_dialog_num = self.count_dialogs_in_batch() - 1

    def are_all_fields_filled(self):
        """check if the turn the annotator is currently on is saved comletly, used before moving to the next turn

        Returns:
            boolean: True if everything is filled, False if not.
        """
        missing_fields = []

        if self.require_rewrite.is_empty():
            missing_fields.append("Requires-Rewrite")

        if self.enough_context.is_empty():
            missing_fields.append("Enough-Context")

        if missing_fields and self.fields_check:
            tk.messagebox.showwarning(
                "Warning",
                "The following fields are missing: "
                + ", ".join(missing_fields)
                + ". Please fill them in before proceeding.",
            )
            return False

        return True

    def save_json(self):
        self.LoadingScreen.show_loading_screen(message="Saving your progress...")
        self.update_json()
        finished = False
        self.LoadingScreen.close_loading_screen()
        if self.mongo.save_to_mongo(self.json_data, self.get_dialog_id()) == False:
            tk.messagebox.showerror(
                "Error",
                "An error occurred while saving the file. Do not close the app, and contact Ori.",
            )
        else:
            finished = True

        if finished == True:
            tk.messagebox.showinfo("Success", "The file was saved successfully.")

    def update_json(self, prev=False):
        """updates the json_file inside the Data class (MongoDB or JsonHandler), to be saved later

        Raises:
            MemoryError: Raises when using online mode, and the annotation was not saved correctly in MongoDB

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        self.json_data = self.require_rewrite.update_json_data(
            self.get_dialog_id(), self.current_turn_num, self.json_data
        )
        self.json_data = self.enough_context.update_json_data(
            self.get_dialog_id(), self.current_turn_num, self.json_data
        )

        return True

    def get_dialog_id(self):
        """simply gets the string of the dialog_id using the current num of the dialog in the batch file

        Returns:
            string: the dialog_id
        """
        return JsonFunctions.get_dialog_id(self.json_data, self.current_dialog_num)

    def init_turn(self):
            """
            Initializes a new turn in the GUI application.

            This method performs the following tasks:
            - Prints the progress string indicating the current turn and dialog number.
            - Updates the current turn and dialog labels in the progress bar.
            - Displays the dialog in the dialog frame.
            - Updates the entry text for the "require rewrite" field.
            - Updates the entry text for the "enough context" field.
            - Updates the font size.
            - Sets focus on the "require rewrite" field.
            - Updates the maximum dialog number if necessary.
            - Updates the status bar.

            Parameters:
            None

            Returns:
            None
            """
            
            progress_string = (
                f"Turn={self.current_turn_num+1} | Dialog={self.current_dialog_num+1}"
            )
            print(progress_string)
            self.save_counter += 1
            self.progress.update_current_turn_dialog_labels(
                self.json_data,
                self.current_dialog_num,
                self.get_dialog_id(),
                self.current_turn_num,
                JsonFunctions.count_turns_in_dialog(self.json_data, self.get_dialog_id()),
            )
            self.dialog_frame.display_dialog(
                self.get_dialog_id(), self.current_turn_num, self.json_data
            )
            self.require_rewrite.update_entry_text(
                self.get_dialog_id(), self.current_turn_num, self.json_data
            )
            self.enough_context.update_entry_text(
                self.get_dialog_id(), self.current_turn_num, self.json_data
            )

            self.font.update_font_size_wrapper()
            self.require_rewrite.focus_on()

            if self.current_dialog_num > self.max_dialog_num:
                self.max_dialog_num = self.current_dialog_num

            self.update_status_bar(self.get_dialog_id())

    def get_first_turn_index(self):
            """
            Returns the index of the first turn in the JSON data for the current dialog.

            Returns:
                int: The index of the first turn.
            """
            
            return JsonFunctions.first_turn(self.json_data, self.get_dialog_id())

    def get_original_question(self):
        """
        Retrieves the original question from the dialog data based on the current turn number.

        Returns:
            str: The original question from the dialog data.
        """
        return JsonFunctions.get_original_question(
            self.json_data, self.get_dialog_id(), self.current_turn_num
        )

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
        return JsonFunctions.count_dialogs_in_batch(self.json_data)

    def prev_turn(self):
        """goes to the previous turn in the dialog
            if there are no more turns, go to the prev dialog,
            if there are no more dialogs and using mongo, goes to prev batch (if offline need to manually change target.json)

        Returns:
            boolean: Return True if opertion was successful, False if not
        """

        if not self.update_json(prev=True):
            return False

        if self.current_turn_num > JsonFunctions.first_turn(
            self.json_data, self.get_dialog_id()
        ):
            self.current_turn_num -= 1
            self.init_turn()

        else:
            self.prev_dialog()

        return True

    def next_turn(self, event=None):
        """goes to the previous turn in the dialog
            if there are no more turns, go to the next dialog,
            if there are no more dialogs and using mongo, goes to next batch (if offline need to manually change target.json)

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        focused_widget = self.root.focus_get()
        
        if focused_widget == self.progress.get_widget():
            self.root.focus_set()
            return True
            

        if not self.are_all_fields_filled():
            return False

        elif not self.update_json():
            return False

        self.mongo.save_json(json_data=self.json_data, dialog_id=self.get_dialog_id())

        if self.current_turn_num < JsonFunctions.last_turn(
            self.json_data, self.get_dialog_id()
        ):
            self.current_turn_num += 1
            self.init_turn()

        else:
            self.next_dialog()

        return True

    def prev_dialog(self):
        """used in the prev dialog button to go to prev dialog"""

        if self.current_dialog_num > 0:
            if not self.require_rewrite.is_empty():
                self.update_json()

            self.current_dialog_num -= 1
            self.current_turn_num = JsonFunctions.last_turn(
                self.json_data, self.get_dialog_id()
            )
            self.init_turn()
            self.font.update_font_size_wrapper()

        else:
            tk.messagebox.showwarning("Warning", "This is the first dialog")

    def next_dialog(self):
        """used in the next dialog button to go to prev dialog"""

        if self.current_dialog_num < len(self.json_data) - 1:
            if self.fields_check:
                if self.are_all_turns_filled():
                    if not self.require_rewrite.is_empty():
                        self.update_json()
                    self.current_dialog_num += 1
                    self.current_turn_num = self.get_first_turn_index()
                    self.init_turn()

                else:
                    tk.messagebox.showwarning(
                        "Warning", "Not all turns in this dialog are filled"
                    )
            else:
                self.update_json()
                self.current_dialog_num += 1
                self.current_turn_num = self.get_first_turn_index()
                self.init_turn()

        else:
            tk.messagebox.showinfo(
                title="Finished Annotating!", message="No More Annotations", icon="info"
            )

    def are_all_turns_filled(self):
        """when going to the next dialog using the button, checks if all the turns in the dialog are filled


        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        turns = JsonFunctions.get_turns(self.json_data, self.get_dialog_id())
        for turn in turns.values():
            if (
                JsonFunctions.get_require_rewrite(
                    self.json_data, self.get_dialog_id(), self.current_turn_num
                )
                is None
            ):
                return False
        return True

    def update_enough_focus_state(self):
        """
        Update the focus state of the 'enough_context' based on the value of 'require_rewrite' choice variable.

        If the 'require_rewrite' choice variable is 0, the 'enough_context' is set to a focused state.
        Otherwise, the 'enough_context' is set to a normal state.

        Args:
            None

        Returns:
            None
        """
        if self.require_rewrite.choice_var.get() == 0:
            self.enough_context.choice_var.set(1)
            self.enough_context.circle1.config(state="disabled")
            self.enough_context.circle2.config(state="disabled")
        else:
            self.enough_context.circle1.config(state="normal")
            self.enough_context.circle2.config(state="normal")
            self.enough_context.choice_var.set(-1)

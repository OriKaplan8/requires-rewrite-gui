from utils import (
    ProgressIndicator,
    FontSizeChanger,
    LoadingScreen,
    DialogFrame,
    MongoData,
)
from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import font
from JsonUtility import JsonUtilityHelper


class BaseAnnotationApp(ABC):

    def __init__(self, root, version, title, connection_string, res=(1200,800), login={}):

        self.root = root
        self.version = version
        self.login = login
        self.title = title
        self.res = res
        self.connection_string = connection_string

        self.setup_main_window()
        self.setup_configurations()
        self.setup_top_panel()
        self.setup_main_pane()
        self.setup_data()
        self.setup_shared_classes()
        self.setup_special_classes()
        self.find_next_empty_turn()
        self.init_turn()

    #region Setup Functions
    def setup_main_window(self):
        self.root.title(self.title)
        self.root.minsize(self.res[0], self.res[1])
        self.root.update()

    def setup_configurations(self):
        # set up settings
        self.fields_check = True
        self.save_before_exit = False
        self.save_counter = 15


        # Override the window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_top_panel(self):
        self.top_panel_frame = tk.Frame(self.root)
        self.top_panel_frame.pack(side=tk.TOP, fill=tk.X) 
        version_label = tk.Label(self.top_panel_frame, text=f"Version {self.version}")
        version_label.pack(side=tk.RIGHT, padx=10, pady=10)
        self.create_navigation_buttons()
        self.create_save_button()
        self.create_status_bar()
        
    def setup_main_pane(self):
        self.main_pane = tk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        self.create_bottom_next_button()
    
    def setup_data(self):
        self.mongo = MongoData(self.root, self.connection_string, self.login)
        self.json_data = self.mongo.load_file()

        if self.json_data == None or self.json_data == "":
            raise Exception(f"The json files is Null.\n JSON={self.json_data}")
        
        # Load JSON and display data
        self.current_dialog_num = 0
        self.current_turn_num = 0
        self.max_dialog_num = 0

    def setup_shared_classes(self):
        self.font = FontSizeChanger(self.top_panel_frame, self.root)
        self.font.add_exclude_widget(self.dialog_label)
        self.progress = ProgressIndicator(self.top_panel_frame, dialog_change_function=self.change_dialog)
        self.dialog_frame = DialogFrame(self.main_pane, self.root)
        self.LoadingScreen = LoadingScreen(self.root)
        self.json = JsonUtilityHelper(self)

    def create_navigation_buttons(self):
        # "<" (Previous) and ">" (Next) buttons next to each other
        prev_button = tk.Button(self.top_panel_frame, text="<", command=self.prev_turn)
        prev_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        next_button = tk.Button(self.top_panel_frame, text=">", command=self.next_turn)
        next_button.pack(side=tk.LEFT)

        # "<<" (Previous Dialog) and ">>" (Next Dialog) buttons
        prev_dialog_button = tk.Button(
            self.top_panel_frame, text="<<", command=self.prev_dialog
        )
        prev_dialog_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        next_dialog_button = tk.Button(
            self.top_panel_frame, text=">>", command=self.next_dialog
        )
        next_dialog_button.pack(side=tk.LEFT)

    def create_save_button(self):
        # Save Button at the top
        self.save_button = tk.Button(
            self.top_panel_frame, text="Save", command=self.save_json
        )
        self.save_button.pack(side=tk.RIGHT, pady=10, padx=(0, 10))

    def create_status_bar(self):
        # Create status bar frame with a darker background color
        self.status_bar = tk.Frame(self.root, bd=1, relief=tk.SUNKEN, height=25, bg="#ebebeb")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.dialog_text = tk.Text(self.status_bar, wrap=tk.WORD, height=1, bg="#ebebeb", bd=0)
        self.dialog_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dialog_text.config(state=tk.DISABLED)
    
        # Create a label for the status bar
        self.dialog_label = tk.Label(self.status_bar, text="", bg="#ebebeb")
        self.dialog_label.pack(side=tk.LEFT, padx=10)
    
    def create_bottom_next_button(self):
        # Next Button at the bottom
        self.bottom_next_button = tk.Button(
            self.root, text="Next Turn", command=self.next_turn
        )
        self.bottom_next_button.pack(side=tk.BOTTOM, pady=10)
        self.root.bind("<Return>", self.next_turn)
    #endregion
    
    #region Main Functions
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
        self.current_turn_num = self.json.get_first_turn()
        self.init_turn()

    def prev_turn(self):
        """goes to the previous turn in the dialog
            if there are no more turns, go to the prev dialog,
            if there are no more dialogs and using mongo, goes to prev batch (if offline need to manually change target.json)

        Returns:
            boolean: Return True if opertion was successful, False if not
        """

        if not self.update_json():
            return False

        if self.current_turn_num > self.json.get_first_turn():
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

        self.mongo.save_json(json_data=self.json_data, dialog_id=self.json.get_dialog_id())

        if self.current_turn_num < self.json.get_last_turn():
            self.current_turn_num += 1
            self.init_turn()

        else:
            self.next_dialog()

        return True
    
    def prev_dialog(self):
        """used in the prev dialog button to go to prev dialog"""

        if self.current_dialog_num > 0:
            self.current_dialog_num -= 1
            self.current_turn_num = self.json.get_last_turn()
            self.init_turn()
            self.font.update_font_size_wrapper()

        else:
            tk.messagebox.showwarning("Warning", "This is the first dialog")

    def next_dialog(self):
        """used in the next dialog button to go to prev dialog"""

        if self.current_dialog_num < len(self.json_data) - 1:
            if self.fields_check:
                if self.are_all_turns_filled():
                    self.update_json()
                    self.current_dialog_num += 1
                    self.current_turn_num = self.json.get_first_turn()
                    self.init_turn()

                else:
                    tk.messagebox.showwarning(
                        "Warning", "Not all turns in this dialog are filled"
                    )
            else:
                self.update_json()
                self.current_dialog_num += 1
                self.current_turn_num = self.json.get_first_turn()
                self.init_turn()

        else:
            tk.messagebox.showinfo(
                title="Finished Annotating!", message="No More Annotations", icon="info"
            )

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
            f"Total Turns: {self.json.count_turns_in_dialog()} | Total Dialogs: {self.json.count_dialogs_in_batch()} | "
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
            self.json.get_dialog_id(),
            self.current_turn_num,
            self.json.count_turns_in_dialog(),
        )

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

    def save_json(self):
        self.LoadingScreen.show_loading_screen(message="Saving your progress...")
        self.update_json()
        finished = False
        self.LoadingScreen.close_loading_screen()
        if self.mongo.save_to_mongo(self.json_data, self.json.get_dialog_id()) == False:
            tk.messagebox.showerror(
                "Error",
                "An error occurred while saving the file. Do not close the app, and contact Ori.",
            )
        else:
            finished = True

        if finished == True:
            tk.messagebox.showinfo("Success", "The file was saved successfully.")

    def find_next_empty_turn(self):
        """goes through the json_file and finds the next turn which is not filled already, then sets the program to show the turn"""
        for dialog_index, dialog_id in enumerate(self.json_data):
            
            turns = self.json.get_turns_by_dialog(dialog_id)

            for turn_key in turns.keys():
                if self.is_turn_empty(dialog_id, int(turn_key)):
                    self.current_dialog_num = dialog_index 
                    self.max_dialog_num = dialog_index 
                    self.current_turn_num = int(turn_key)
                    return

        self.current_dialog_num = self.json.count_dialogs_in_batch() - 1
        self.current_turn_num = self.json.count_turns_in_dialog()  
        self.max_dialog_num = self.json.count_dialogs_in_batch() - 1

    def init_turn(self):
       
            progress_string = (
                f"Turn={self.current_turn_num} | Dialog={self.current_dialog_num+1}"
            )
            print(progress_string)
            self.save_counter += 1
            self.progress.update_current_turn_dialog_labels(
                self.json_data,
                self.current_dialog_num,
                self.json.get_dialog_id(),
                self.current_turn_num,
                self.json.count_turns_in_dialog(),
            )
            self.dialog_frame.display_dialog(
                self.json.get_dialog_id(), self.current_turn_num, self.json_data
            )
            self.font.update_font_size_wrapper()
            if self.current_dialog_num > self.max_dialog_num:
                self.max_dialog_num = self.current_dialog_num

            self.init_turn_special_classes()
            
            self.font.update_font_size_wrapper()
            self.update_status_bar(self.json.get_dialog_id())

    def are_all_turns_filled(self):
        """when going to the next dialog using the button, checks if all the turns in the dialog are filled


        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        turns = self.json.get_turns_in_current_dialog()
        for turn_num in turns.keys():
            if self.is_turn_empty(self.json.get_dialog_id(), turn_num):
                return False
        return True
    #endregion
   
    #region Abstract Functions  
    @abstractmethod
    def is_turn_empty(self, dialog_id, turn_num):
        pass
    
    @abstractmethod
    def are_all_fields_filled(self):
        pass
       
    @abstractmethod
    def setup_special_classes(self):
        pass
    
    @abstractmethod
    def init_turn_special_classes(self):
        pass
    
    @abstractmethod
    def update_json(self):
        pass
    #endregion
    

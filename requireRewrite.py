from baseAnnotationApp import BaseAnnotationApp
import tkinter as tk
from utils import RequireRewriteCheckBox, NeedsClarificationCheckBox, EnoughContext


class requireRewrite(BaseAnnotationApp):

    def is_turn_empty(self, dialog_id, turn_id):
       
        if self.json.get_require_rewrite_by_dialog_and_turn(dialog_id, turn_id) is None:
           
            return True
        
        return False

    def are_all_fields_filled(self):
        """check if the turn the annotator is currently on is saved comletly, used before moving to the next turn

        Returns:
            boolean: True if everything is filled, False if not.
        """
        missing_fields = []

        if self.require_rewrite.is_empty():
            missing_fields.append("Requires-Rewrite")

        if self.require_rewrite.get_requires_rewrite() != 0:
            if self.enough_context.is_empty():
                missing_fields.append("Enough-Context")
                
            if self.needs_clarification:
                if self.needs_clarification.is_empty():
                    missing_fields.append("Needs-Clarification")

        if missing_fields and self.fields_check:
            tk.messagebox.showwarning(
                "Warning",
                "The following fields are missing: "
                + ", ".join(missing_fields)
                + ". Please fill them in before proceeding.",
            )
            return False

        return True
    
    def setup_special_classes(self):
        self.require_rewrite = RequireRewriteCheckBox(
            self.main_pane, self.root, self.update_enough_focus_needs_clarification_state
        )
        self.enough_context = EnoughContext(self.main_pane, self.root)
        self.needs_clarification = None

        if self.mongo.get_needs_clarification():
            self.needs_clarification = NeedsClarificationCheckBox(self.main_pane, self.root)
 
    def init_turn_special_classes(self):
        self.require_rewrite.update_entry_text(
                self.json.get_dialog_id(), self.current_turn_num, self.json_data
            )

        self.enough_context.update_entry_text(
                
                self.json.get_dialog_id(), self.current_turn_num, self.json_data
            )

        if self.needs_clarification: # If the needs_clarification field is present
                self.needs_clarification.update_entry_text(
                    
                    self.json.get_dialog_id(), self.current_turn_num, self.json_data
                )

    def update_enough_focus_needs_clarification_state(self):
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
            self.enough_context.choice_var.set(-1)
            self.enough_context.circle1.config(state="disabled")
            self.enough_context.circle2.config(state="disabled")
            
            if self.needs_clarification:
                self.needs_clarification.choice_var.set(-1)
                self.needs_clarification.circle1.config(state="disabled")
                self.needs_clarification.circle2.config(state="disabled")
                
        else:
            self.enough_context.circle1.config(state="normal")
            self.enough_context.circle2.config(state="normal")
            self.enough_context.choice_var.set(-1)
            
            if self.needs_clarification:
                self.needs_clarification.circle1.config(state="normal")
                self.needs_clarification.circle2.config(state="normal")
                self.needs_clarification.choice_var.set(-1)

    def update_json(self):
        """updates the json_file inside the Data class (MongoDB or JsonHandler), to be saved later

        Raises:
            MemoryError: Raises when using online mode, and the annotation was not saved correctly in MongoDB

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        self.json_data = self.require_rewrite.update_json_data(
            self.json.get_dialog_id(), self.current_turn_num, self.json_data
        )
        self.json_data = self.enough_context.update_json_data(
            self.json.get_dialog_id(), self.current_turn_num, self.json_data
        )
        
        if self.needs_clarification:
            self.json_data = self.needs_clarification.update_json_data(
                self.json.get_dialog_id(), self.current_turn_num, self.json_data
            )

        return True
from jsonFunctions import JsonFunctions as jf



class JsonUtilityHelper:
    def __init__(self, base_app):
        self.base_app = base_app 
        
    def get_dialog_id(self):
        return jf.get_dialog_id(self.base_app.json_data, self.base_app.current_dialog_num)
    
    def count_turns_in_dialog(self):
        """count the number of turn in the dialog

        Returns:
            int: number of turns in dialog
        """
        return jf.count_turns_in_dialog(self.base_app.json_data, self.get_dialog_id())
    
    def count_dialogs_in_batch(self):
        """count the number of dialogs in the batch file

        Returns:
            int: number of dialogs in batch
        """
        return jf.count_dialogs_in_batch(self.base_app.json_data)
    
    def get_first_turn(self):
        return jf.first_turn(self.base_app.json_data, self.get_dialog_id())
    
    def get_last_turn(self):
        return jf.last_turn(self.base_app.json_data, self.get_dialog_id())

    def get_turns_in_current_dialog(self):
        return jf.get_turns(self.base_app.json_data, self.get_dialog_id())
    
    def get_require_rewrite(self, key):
        return jf.get_require_rewrite(self.base_app.json_data, self.get_dialog_id(), key)
    
    def get_turn_by_turn_num(self, turn_num):
        return jf.get_turn(self.base_app.json_data, self.get_dialog_id(), turn_num)
    
    def get_require_rewrite_by_dialog_and_turn(self, dialog_id, turn_num):
       
        return jf.get_require_rewrite(self.base_app.json_data, dialog_id, turn_num)
    
    def get_enough_context_by_dialog_and_turn(self,dialog_id, key):
        return jf.get_context(self.base_app.json_data,dialog_id, key)
    
    def get_turns_by_dialog(self, dialog_id):
        return jf.get_turns(self.base_app.json_data, dialog_id)



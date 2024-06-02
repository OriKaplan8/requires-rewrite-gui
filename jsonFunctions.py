class JsonFunctions:

    def get_turn(json_data, dialog_id, turn_num):

        return json_data[dialog_id]['dialog'][str(turn_num)]
        
    
    
    def set_turn(json_data, dialog_id, turn_num, new_turn_data):
        json_data[dialog_id]['dialog'][str(turn_num)] = new_turn_data
        return json_data
    
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
        turn_data = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        field = ""
        if "requires_rewrite" in turn_data.keys():
            field = "requires_rewrite"
        elif "requires rewrite" in turn_data.keys():
            field = "requires rewrite"
        else:
            raise Exception(
                f"requires_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys_found = {turn_data.keys()}"
            )

        return turn_data[field]

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
        turn_data = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        field = ""
        if "annotator_rewrite" in turn_data.keys():
            field = "annotator_rewrite"
        if "annotator rewrite" in turn_data.keys():
            field = "annotator rewrite"
        else:
            raise Exception(
                f"annotator_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys_found = {turn_data.keys()}"
            )

        return turn_data[field]

    def get_turns(json_data, dialog_id, only_annotatable=True):
        turns = {}
        start = 1 if only_annotatable else 0

        number_of_turns = JsonFunctions.count_turns_in_dialog(json_data, dialog_id, only_annotatable)
        

            
        for i in range(start, number_of_turns + 1):
            turns[str(i)] = JsonFunctions.get_turn(json_data, dialog_id, i)

    
        return turns

    def count_turns_in_dialog(json_data, dialog_id, only_annotatable=True):
        """
        Counts the number of turns in a dialog.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.

        Returns:
        - The number of turns in the dialog.
        """

        return json_data[dialog_id]["number_of_turns"] - 1

    

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
        return JsonFunctions.get_turn(json_data, dialog_id, turn_num)["original_question"]
       
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
        turn_data = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        field = ""
        if "requires_rewrite" in turn_data.keys():
            field = "requires_rewrite"
        elif "requires rewrite" in turn_data.keys():
            field = "requires rewrite"
        else:
            raise Exception(
                f"requires_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys found: {turn_data.keys()}"
            )

        if new_value == -1:
            new_value = None

        turn_data[field] = new_value

        return JsonFunctions.set_turn(json_data, dialog_id, turn_num, turn_data)

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
        turn_data = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        return turn_data["enough_context"]

    def change_context(json_data, dialog_id, turn_num, new_value):
        turn_data = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        if new_value == -1:
            new_value = None

        turn_data["enough_context"] = new_value

        return JsonFunctions.set_turn(json_data, dialog_id, turn_num, turn_data)

    def get_dialog_id(json_data, dialog_num):
        return list(json_data.keys())[dialog_num]

    def count_dialogs_in_batch(json_data):
        return len(json_data)
    
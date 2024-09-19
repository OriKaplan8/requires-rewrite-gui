import random
from shared_utils import compare_norm_texts

class JsonFunctions:

    def get_turn(json_data, dialog_id, turn_num):
        
        try:
            return json_data[dialog_id]['dialog'][str(turn_num)]
        
        except:
            raise Exception(f"Dialog ID {dialog_id} and turn number {turn_num} not found in JSON data.\nDialog IDs: {json_data[dialog_id]['dialog'].keys()}")
        
        
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
    
    def get_needs_clarification(json_data, dialog_id, turn_num):
        """
        Retrieves the value of the 'needs_clarification' field from the given JSON data.

        Args:
            json_data (dict): The JSON data containing the dialog information.
            dialog_id (str): The ID of the dialog.
            turn_num (int): The turn number.

        Returns:
            The value of the 'needs_clarification' field.

        Raises:
            Exception: If the 'needs_clarification' field is not found in the dialog data.
        """

        turn_data = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        field = ""
        if "needs_clarification" in turn_data.keys():
            field = "needs_clarification"
        elif "needs clarification" in turn_data.keys():
            field = "needs clarification"
        else:
            raise Exception(
                f"needs_clarification field not found in dialog_id={dialog_id} and turn_num={turn_num} | keys_found = {turn_data.keys()}"
            )

        return turn_data[field]

    def change_needs_clarification(json_data, dialog_id, turn_num, new_value):
        turn_data = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        if new_value == -1:
            new_value = None

        turn_data["needs_clarification"] = new_value

        return JsonFunctions.set_turn(json_data, dialog_id, turn_num, turn_data)

    def get_turns(json_data, dialog_id, only_annotatable=True, fitered_for_rewrite_scoring=False):
        turns = {}
        start = 1 if only_annotatable else 0

        number_of_turns = JsonFunctions.count_turns_in_dialog(json_data, dialog_id, only_annotatable)
        
        for i in range(start, number_of_turns + 1):
            turns[str(i)] = JsonFunctions.get_turn(json_data, dialog_id, i)

        if fitered_for_rewrite_scoring:
            turns = JsonFunctions.filter_for_rewrite_scoring_annotation(json_data, dialog_id ,turns)

    
        return turns
    
    def filter_for_rewrite_scoring_annotation(json_data, dialog_id, turns):
        filtered_turns = {}

        for turn_num in turns.keys():
            if JsonFunctions.is_turn_annotatable_rewrite_scoring(json_data, dialog_id, turn_num):
                filtered_turns[turn_num] = turns[turn_num]

        return filtered_turns
    
    def is_turn_annotatable_rewrite_scoring(json_data, dialog_id, turn_num):
        turn_valid = False
        rewrites = JsonFunctions.get_rewrites(json_data, dialog_id, turn_num)
        for key1, rewrite1 in rewrites.items():
            for key2, rewrite2 in rewrites.items():
                if key1 != key2:
                    if not compare_norm_texts(rewrite1['text'], rewrite2['text']):
                        turn_valid = True
                        break
        return turn_valid

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
        turn = JsonFunctions.get_turn(json_data, dialog_id, turn_num)
        rewrites = {}

        for key, value in turn["models_rewrites"].items():
                rewrites[key] = value

        return dict(random.sample(list(rewrites.items()), len(rewrites)))
    
    def get_rewrite(json_data, dialog_id, turn_num, rewrite_num):
        rewrites = JsonFunctions.get_rewrites(json_data, dialog_id, turn_num)

        return rewrites[rewrite_num]
    
    def get_score(json_data, dialog_id, turn_num, rewrite_num):
        rewrite = JsonFunctions.get_rewrite(json_data, dialog_id, turn_num, rewrite_num)

        return rewrite["score"]
    
    def get_optimal(json_data, dialog_id, turn_num, rewrite_num):
        rewrite = JsonFunctions.get_rewrite(json_data, dialog_id, turn_num, rewrite_num)

        return rewrite["optimal"]
    
    def set_score(json_data, dialog_id, turn_num, rewrite_num, new_score):
        turn = JsonFunctions.get_turn(json_data, dialog_id, turn_num)
        try:
            turn["models_rewrites"][rewrite_num]["score"] = new_score
        except:
            raise Exception(f"Rewrite id {rewrite_num} not found in turn {turn_num}. Existing rewrites: {turn['models_rewrites'].keys()}")
        return JsonFunctions.set_turn(json_data, dialog_id, turn_num, turn)
    
    def set_optimal(json_data, dialog_id, turn_num, rewrite_num, new_optimal):
        turn = JsonFunctions.get_turn(json_data, dialog_id, turn_num)
        turn["models_rewrites"][rewrite_num]["optimal"] = new_optimal
        return JsonFunctions.set_turn(json_data, dialog_id, turn_num, turn)

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

        turn = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        field = ''
        if 'annotator_rewrite' in turn.keys():
            field = 'annotator_rewrite'
        elif 'annotator rewrite' in turn.keys():
            field = 'annotator rewrite'
        else:
            raise Exception(f"annotator_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num}.  Existing fields: {[f for f in JsonFunctions.get_turn(json_data,dialog_id,turn_num)]}")
        
        turn[field] = new_value

        json_data = JsonFunctions.set_turn(json_data, dialog_id, turn_num, turn)

        return json_data
    
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
        if field == "optimal":
            return JsonFunctions.set_optimal(json_data, dialog_id, turn_num, rewrite_key, new_value)
        elif field == "score":
            return JsonFunctions.set_score(json_data, dialog_id, turn_num, rewrite_key, new_value)
        else:
            raise Exception(f"Rewrite field {field} was not found in turn. Existing fields: {[f for f in JsonFunctions.get_turn(json_data,dialog_id,turn_num)]}")
      
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
        turn = JsonFunctions.get_turn(json_data, dialog_id, turn_num)
        field = ''
        if 'annotator_rewrite' in turn.keys():
            field = 'annotator_rewrite'
        elif 'annotator rewrite' in turn.keys():
            field = 'annotator rewrite'
        else:
            raise Exception(f"annotator_rewrite field not found in dialog_id={dialog_id} and turn_num={turn_num}. fields: {turn.keys()}")
        
        
        return turn[field]
        
    def all_rewrites_filled(json_data, dialog_id, turn_num):
        """
        Checks if all rewrites have been filled in the JSON data.

        Parameters:
        - json_data: The JSON data.
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.

        Returns:
        - True if all rewrites have been filled; False otherwise.
        """
        turn = JsonFunctions.get_turn(json_data, dialog_id, turn_num)

        for key, value in turn["models_rewrites"].items():
            if value["optimal"] == None or value["score"] == None:
                return False

        return True
    

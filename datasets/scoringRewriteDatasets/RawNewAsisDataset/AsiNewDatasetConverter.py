import os
import json
import math

def read_json(file):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Build the full path to the file
    file_path = os.path.join(script_dir, file)
    with open(file_path) as f:
        return json.load(f)

def convert_sets(obj):
    """Recursively convert sets to lists in the data structure."""
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: convert_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets(i) for i in obj]
    else:
        return obj

def save_json(file, data):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Build the full path to the file
    file_path = os.path.join(script_dir, file)
    
    # Convert sets to lists (since sets are not JSON serializable)
    data = convert_sets(data)
    
    try:
        # Save JSON data with indentation for better readability
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"File saved successfully to {file_path}")
    except TypeError as e:
        print(f"Error: Could not serialize data. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def is_dialog_valid(dialog_data, dialog_index):
    speakers = get_speakers_list(dialog_data)
    for turn_index in range(len(dialog_data)):
        current_dict = dialog_data[turn_index]
        speaker = current_dict.get("speaker", None)
        
        if turn_index % 2 == 0 and speaker != "assistant":
            
            print(f"Speaker Error in dialog {dialog_index}: Expected 'assistant' at turn {turn_index}, but got '{speaker}'")
            
            return False
        
        if turn_index % 2 == 1 and speaker != "user":
            
            print(f"Speaker Error in dialog {dialog_index}: Expected 'user' at turn {turn_index}, but got '{speaker}'")
            
            return False
        
        if speakers[-1] == "user":
            #print("User is the last speaker, but thats no problem")
            pass

    return True

def check_json(json_list):
    for dialog_index, dialog_data in enumerate(json_list):
        is_dialog_valid(dialog_data, dialog_index)

def get_speakers_list(dialog_data):
    speakers = [entry["speaker"] for entry in dialog_data]
    return speakers

def print_dialog(dialog_data):
    for turn_index in range(0, len(dialog_data)):
        entry = dialog_data[turn_index]
        print(f'{entry["speaker"]}:\n{json.dumps(entry, indent=4)}\n')

def process_json(json_list):
    json_converted_data = {}
    for dialog_index, dialog_data in enumerate(json_list):

        if is_dialog_valid(dialog_data, dialog_index):
            json_converted_data[dialog_data[0]["chat_id"]] = process_dialog(dialog_data)         
    
    return json_converted_data
            
def process_dialog(dialog_data):
    dialog_converted_data = {"number_of_turns": 0,
                   "annotator_id": None,
                   "dialog": {"0" : process_intro(dialog_data[0])}}
    
    turn_counter = 1
    
    for turn_index in range(1, len(dialog_data), 2):
        assistant_turn, user_turn = None, None

        user_turn = dialog_data[turn_index]

        if turn_index + 1 < len(dialog_data):
            assistant_turn = dialog_data[turn_index + 1]

        else:
            assistant_turn = None

        dialog_converted_data["dialog"][turn_counter] = process_turn(user_turn, assistant_turn, turn_counter)
        turn_counter += 1


    dialog_converted_data["number_of_turns"] = turn_counter
    return dialog_converted_data

def process_intro(assistant_turn):
    return{
        "turn_num": 0,
        "original_question": assistant_turn["utr"],
        "answer": "",
        "info": {
            "chat_id": assistant_turn["chat_id"],
            "agent_name": assistant_turn["agent_name"],
            "user_info": {
                "id": None,
                "utr_num": None,
                "DcR_score": None,
            },
            "assistant_info": {
                "id": assistant_turn["id"],
                "utr_num": assistant_turn["utr_num"],
            },
        },
        
    }

def process_turn(user_turn, assistant_turn, turn_counter ):
    if assistant_turn is not None:
        return {
            "turn_num": turn_counter,
            "original_question": user_turn["utr"],
            "answer": assistant_turn["utr"],
            "info": {
                "chat_id": user_turn["chat_id"],
                "agent_name": assistant_turn["agent_name"],
                
                "user_info": {
                    "id": user_turn["id"],
                    "utr_num": user_turn["utr_num"],
                    "DcR_score": user_turn["DcR_score"],
                },
                "assistant_info": {
                    "id": assistant_turn["id"],
                    "utr_num": assistant_turn["utr_num"],
                },
        
            },
            "requires_rewrite": None,
            "models_rewrites": process_rewrites(user_turn)
        }
    else:
        return {
            "turn_num": user_turn["utr_num"],
            "original_question": user_turn["utr"],
            "answer": None,
            "info": {
                "chat_id": user_turn["chat_id"],
                "agent_name": user_turn["agent_name"],
                
                "user_info": {
                    "id": user_turn["id"],
                    "utr_num": user_turn["utr_num"],
                    "DcR_score": user_turn["DcR_score"],
                },
                "assistant_info": {
                    None,
                },
        
            },
            "requires_rewrite": None,
            "models_rewrites": process_rewrites(user_turn)
        }

def process_rewrites(user_turn):
    rewrites_dict = {}
    rewrite_keys = ["prod_rewite", "DcR_rewrite"]
    for key, value in user_turn.items():
       if key in rewrite_keys:
           if value is not None:
            rewrites_dict[key] = {
                "text": value,
                "score": None,
                "optimal": None
            }
    return rewrites_dict
           

        


# Use the JSON file in the script's directory
json_data = read_json("comparison_17_9.json")
converted_json_data = process_json(json_data)
save_json("converted_new_asi_data.json", converted_json_data)

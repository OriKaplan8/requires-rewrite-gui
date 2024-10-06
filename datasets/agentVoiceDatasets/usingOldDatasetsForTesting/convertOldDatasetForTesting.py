import json
import os

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the JSON file
json_file_path = os.path.join(script_dir, 'json_rewrites.json')


def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)



def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def convertJson(json_data):
    new_json = {}

    for dialog_key, dialog_value in json_data.items():
        
        dialog = {
            "number_of_turns": dialog_value["number_of_turns"],
            "annotator_id": None,
            "dialog": {}
        }

        for dialog_turn_i, dialog_turn_value in enumerate(dialog_value["dialog"]):

            if dialog_turn_i == 0:
                turn = {
                    "turn_num": dialog_turn_i,
                    "original_question": dialog_turn_value["original_question"],
                    "answer": dialog_turn_value["answer"],

                }
                dialog["dialog"][dialog_turn_i] = turn
                continue
            
            else:

                turn = {
                    "turn_num": dialog_turn_i,
                    "original_question": dialog_turn_value["original_question"],
                    "answer": dialog_turn_value["answer"],
                    "annotations": None,
                }
                

            dialog["dialog"][str(dialog_turn_i)] = turn  # dialog_i is the index for each turn
            
        new_json[dialog_key] = dialog

    return new_json



json_data = read_json(json_file_path)
new_json = convertJson(json_data)
write_json("old_dataset_converted_voice_agent_testing.json", new_json)
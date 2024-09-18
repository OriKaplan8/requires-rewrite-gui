import random
import json

def save_json_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        
        
def create_toy_rewrite_dict(dialog_n, turn_n, rewrite_n):
    if random.choice([True,True, False]):
        text = f"this is rewrite_{dialog_n}_{turn_n}_{rewrite_n}"
    else:
        text = f"original_question_{dialog_n}_{turn_n}"
    return {
        "text": text,
        "score": None,
        "optimal": None
    }
    
def create_toy_turn_dict(dialog_n, turn_n, max_rewrites=3):
    number_of_rewrites = random.randint(2, max_rewrites+1)
    rewrites = {}
    for i in range(number_of_rewrites):
        rewrites[i] = create_toy_rewrite_dict(dialog_n, turn_n, i)
        
    return {"turn_num": turn_n,
            "original_question": f"original_question_{dialog_n}_{turn_n}",
            "answer": f"answer_{dialog_n}_{turn_n}",
            "requires_rewrite": None,
            "models_rewrites": rewrites}

def create_toy_dialog_dict(dialog_n, max_turns=5):
    dialog = {"number_of_turns": random.randint(2, max_turns+1),
              "annotator_id": None,
              "dialog": {
                  0 :{
                    "turn_num" : 0,
                    "original_question": f"original_question_{dialog_n}_0",
                    "answer": f"answer_{dialog_n}_0" }
                } 
            }
    
    for i in range(1, dialog["number_of_turns"]):
        dialog["dialog"][i] = create_toy_turn_dict(dialog_n, i)
    
    return dialog
    
    
def create_toy_dataset(num_dialogs, num_turns_per_dialog):
    data = {}
    for i in range(num_dialogs):
        dialog_id = f"dialog_{i}"
        data[dialog_id] = create_toy_dialog_dict(i, num_turns_per_dialog)
    return data


def generate_toy_dataset(num_dialogs, num_turns_per_dialog):
    data = create_toy_dataset(num_dialogs, num_turns_per_dialog)
    save_json_file(data, "toy_dataset_no_ant_r.json")
    
generate_toy_dataset(5, 5)
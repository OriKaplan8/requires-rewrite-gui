import json


def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)



def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def convertJson(json_data):
    new_json = {}

    for key, value in json_data.items():
        dialog = {
            "number_of_turns": value["number_of_turns"],
            "annotator_id": None,
            "dialog": {}
        }

        for dialog_i, dialogValue in enumerate(value["dialog"]):

            if dialog_i == 0:
                turn = {
                    "turn_num": dialog_i,
                    "original_question": dialogValue["original_question"],
                    "answer": dialogValue["answer"],

                }
                dialog["dialog"][dialog_i] = turn
                continue

            turn = {
                "turn_num": dialog_i,
                "original_question": dialogValue["original_question"],
                "answer": dialogValue["answer"],
                "requires_rewrite": None,
                "annotator_rewrite": None,
                "models_rewrites": {}
            }

            for turn_key, turn_value in value.items():
                
                turn["requires_rewrite"] = dialogValue["requires_rewrite"]
                turn["annotator_rewrite"] = dialogValue["annotator_rewrite"]
                
                # Extract model rewrites if available
                for rewrite_key, rewrite_value in value.items():
                    if rewrite_key not in ["requires_rewrite", "annotator_rewrite", "turn_num", "original_question", "answer"]:
                        turn["models_rewrites"][rewrite_key] = {
                            "text": rewrite_value["text"],
                            "score": rewrite_value["score"],
                            "optimal": rewrite_value["optimal"]
                        }

            dialog["dialog"][dialog_i] = turn  # dialog_i is the index for each turn
        new_json[key] = dialog

    return new_json


json_data = read_json("C:\\Users\\User\Projects\\requires-rewrite-gui\\datasets\\scoringRewriteDatasets\\RawOldAsisDataset\\json_rewrites.json")
new_json = convertJson(json_data)
write_json("json_rewrites_converted.json", new_json)
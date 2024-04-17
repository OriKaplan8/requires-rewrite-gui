## Note for Users

This GitHub repository is intended for use by administrators. Annotators can only receive the executable (`exe`) file and do not require access to the source code or any other files hosted here. 


## Getting Started

This section guides you through setting up and starting the Require-rewrite-context-gui program, designed for annotating 'requires rewrite' and 'enough context' fields.

### Installation

Download the executable file (`.exe`) to your computer. Once downloaded, simply double-click the file to launch the program. Upon opening, you will be prompted to enter a name and a `file_id`. 

### Using the Program

To annotate the `asi` dataset:
1. Enter the filename `asi-14_4` in the filename prompt.
2. Provide a username. This username will be associated with your annotations, allowing for personalized data tracking.

### Reviewing Annotations

To view your annotations or those made by other annotators:
- Use the `mongo_data_manager.ipynb` notebook. This notebook contains a function called `retrieve_annotation_by_user_and_file_id`, which you can run with the desired filename and username to retrieve the relevant annotations.

Further details and functions are explained within the notebook itself.

## Repository Files

### `annotation_sources_asi`
This folder contains the original `.xlsx` file provided by ASI, along with a `.json` file that was created from the Excel data. 

### `annotation_requires_rewrite_gui.ipynb`
This Jupyter Notebook contains the source code for the Require-rewrite-context-gui software. It includes detailed explanations of each function used within the software.


## JSON Structure Description

The JSON object represents a dialog structure with annotations. The primary key `dialog` serves as the root level, containing details about conversational turns and annotations. Here is the structure and description of each field within the JSON:

### Root Level

- `<dialog_id>` (`dict`): Contains the details of each turn in the conversation and serves as the root level of the structure.

### <dialog_id> Fields

- `number_of_turns` (`integer`): Indicates the total number of turns in the dialog.
- `annotator_id` (`string` or `null`): The annotator's username, filled automatically when entered in the software's username prompt. If `null`, it hasn't been filled yet.
- `dialog` (`list` of `dict`): Details of each turn in the dialog, as outlined below.
- `turn_num` (`dict`): Key-value pairs representing specific turns that can be annotated. These fields are indexed by numbers. Structure and field types are detailed below.

### Dialog Fields

Within the `dialog` list, each dictionary represents a turn and includes the following fields:

- `turn_num` (`integer`): The sequential number of the turn within the dialog.
- `sample_id` (`string`): A unique identifier for the dialog turn.
- `original_question` (`string`): The original question asked in the turn.
- `answer` (`string`): The answer provided in the turn.

### <turn_num> - Annotatable Turns

This section includes additional annotation fields for certain turns:

- `sample_id` (`string`): A unique identifier for the dialog turn.
- `requires_rewrite` (`boolean` or `null`): Indicates whether the turn requires rewriting. If `null`, it indicates that the field has not been filled in yet.
- `enough_context` (`boolean` or `null`): Determines whether the turn has enough context for rewrites. If `null`, it indicates that the field has not been filled in yet.

Here's a sample JSON snippet for quick reference:

```json
{
  "dialog": [
    {
      "turn_num": 0,
      "sample_id": "QReCC-Train_1102_1",
      "original_question": "Why did Gavin leave Titãs?",
      "answer": "Gavin stated that he was physically and mentally exhausted because of the Titas tours and album releases."
    },
    {
      "turn_num": 1,
      "sample_id": "QReCC-Train_1102_2",
      "original_question": "Did they replace him with anyone?",
      "answer": "Yes, Drummer Mario Fabre, who has remained with the Titas since then as a session member."
    }
  ],
  "number_of_turns": 2,
  "annotator_id": null,
  "1": {
    "sample_id": "QReCC-Train_1102_2",
    "requires_rewrite": null,
    "enough_context": null
  }
}

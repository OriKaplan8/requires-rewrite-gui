# Annotation Program Documentation

This repository is intended for administrators. Annotators only need the executable (`.exe`) file and do not require access to other files.

## File Structure

The code has been refactored and organized into smaller files for better maintainability and readability:

- **utils**: Classes used by the main application, including frontend and backend classes.
- **app**: Main application code, including the primary function that runs the program.
- **jsonFunctions**: Functions to handle JSON files retrieved from MongoDB for reading and writing JSON data.
- **db**: Functions for administrators to manage annotations made by annotators (formerly `mongo_data_manager`).
- **main**: Run this file to start the application.

## Getting Started

### Installation

1. Download the executable file (`.exe`) to your computer.
2. Double-click the file to launch the program.
3. Enter your `username` and the `filename` of the dataset you wish to annotate.

### Using the Program

1. Choose a dataset from the following options:
   - asi-14_4
   - asi-23_4
   - agent_conv_1
   - agent_conv_2
   - agent_conv_3
   - agent_conv_4
2. Enter the chosen filename in the `filename` prompt.
3. Provide a username to associate with your annotations for personalized data tracking.

### Reviewing Annotations

To view annotations:

1. Use the `db.py` file (formerly `mongo_data_manager.ipynb`).
2. Run the `retrieve_annotation_by_user_and_file_id` function with the desired filename and username to retrieve annotations.

## Repository Files

### `annotation_sources`

- **asi**: Contains the original `.xlsx` file provided by ASI and the generated `.json` file.
- **yael**: Contains the original `.xlsx` file provided by YAEL and the generated `.json` file.

## JSON Structure

The JSON object represents a dialog structure with annotations. The primary key `dialog` serves as the root level, containing details about conversational turns and annotations.

### Structure

- `<dialog_id>`: Contains the details of each dialog in the dataset.
  - **number_of_turns**: Total number of turns in the dialog.
  - **annotator_id**: Annotator's username, filled automatically when entered in the software's username prompt (or `null` if not filled).
  - **dialog**: Details of each turn in the dialog.

#### Turn Details

Each turn within the `dialog` dictionary includes:

- **turn_num**: Sequential number of the turn.
- **sample_id**: Unique identifier for the dialog turn.
- **original_question**: The original question asked in the turn.
- **answer**: The answer provided in the turn.
- **requires_rewrite**: Indicates whether the turn requires rewriting (`boolean` or `null`).
- **enough_context**: Determines whether the turn has enough context for rewrites (`boolean` or `null`).

### Example JSON

```json
{
  'QReCC-Train_514': {
    'number_of_turns': 3,
    'annotator_id': null,
    'dialog': {
      '0': {
        'turn_num': 0,
        'sample_id': 'QReCC-Train_514_1',
        'original_question': "What is Symphony X's Iconoclast?",
        'answer': 'Iconoclast is the eighth album by American progressive metal band Symphony X.'
      },
      '1': {
        'turn_num': 1,
        'sample_id': 'QReCC-Train_514_2',
        'original_question': 'When was it released?',
        'answer': "Symphony X's Iconoclast was released on June 17, 2011, in Europe, June 21, 2011, in the United States and on June 28, 2011, in Canada.",
        'requires_rewrite': null,
        'enough_context': null
      },
      '2': {
        'turn_num': 2,
        'sample_id': 'QReCC-Train_514_3',
        'original_question': 'Did it do well on the charts?',
        'answer': "Symphony X's Iconoclast debuted at number 76 on the Billboard 200 album chart in the United States, selling more than 7,300 copies in its first week.",
        'requires_rewrite': null,
        'enough_context': null
      }
    }
  }
}
```

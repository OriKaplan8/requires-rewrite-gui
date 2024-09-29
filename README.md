# Annotation Program Documentation

This repository is intended for administrators. Annotators only need the executable (`.exe`) file and do not require access to other files.

## File Structure

The code has been refactored and organized into smaller files for better maintainability and readability:

- **utils**: Classes used by the main application, including frontend and backend classes.
- **shared_utils**: Classes used by the jsonFunctions and utils, including frontend and backend classes.
- **requiresRewrite**: Main application code, for handling require_rewrites annotations.
- **scoringRewrite**:Main application code, for handling rewrite scoring.
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
   - agent_conv_test
   - agent_conv_complete
   - rewrite-scoring
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
  
## Require Rewrite

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

## Scoring Rewrites

#### Turn Details

Each turn within the `dialog` dictionary includes:

- **turn_num**: Sequential number of the turn.
- **sample_id**: Unique identifier for the dialog turn.
- **original_question**: The original question asked in the turn.
- **answer**: The answer provided in the turn.
- **requires_rewrite**: Indicates whether the turn requires rewriting (`boolean` or `null`).
- **models_rewrites**: Dict of the rewrites including their text and annotation (score and optimal)
- **info**: hold the info from the original dataset of Asi


### Example JSON

```},
    "chat_80af7a83-132c-467f-b8f1-fa342a3ab8ba": {
        "number_of_turns": 2,
        "annotator_id": null,
        "dialog": {
            "0": {
                "turn_num": 0,
                "original_question": "Hi! I'm BIGVU's AI support bot. \nHow can I help you today?",
                "answer": "",
                "info": {
                    "chat_id": "chat_80af7a83-132c-467f-b8f1-fa342a3ab8ba",
                    "agent_name": "bigvu-expert",
                    "user_info": {
                        "id": null,
                        "utr_num": null,
                        "DcR_score": null
                    },
                    "assistant_info": {
                        "id": "assistant_0_chat_80af7a83-132c-467f-b8f1-fa342a3ab8ba",
                        "utr_num": 0
                    }
                }
            },
            "1": {
                "turn_num": 1,
                "original_question": "can i download a BigVU recorded video to my computer, iPad or iPhone?",
                "answer": "Yes, you can download a BIGVU recorded video to your computer, iPad, or iPhone. Here\u2019s how you can do it:\n\n### Download to Your Computer\n1. **Unedited (Script) Project**:\n   - Select the Script project video you want to download.\n   - Click on the 3 dots and choose \"Edit\".\n   - In the take screen, choose the take you want to download by clicking on the 3-dot menu.\n   - Select \"Download\" and choose the format: MP4 or WebM.\n\n2.\n\n**Edited (Video Maker) Project**:\n   - Click on the 3 dots menu of the Video Maker Project and select \"Download\".\n   - Choose the type of file you wish to download: MP4 or WebM.\n\n### Download to Your iPad or iPhone\n1. **Using the Mobile App**:\n   - Access the Projects page (bottom left icon).\n   - Choose the video you want to download.\n   - On the next screen, select the video take you will be sharing.\n   - Click the share button at the bottom of the screen.\n   - Choose \"Download File\" to download your video to your device.\n\n*[Try it now on your project? it's free!](https://bigvu.sng.link/Db284/ot3k?wpsrc=button&_smtype=3&utm_medium=chatbot&utm_source=bigvu.tv&utm_content=ai_script&utm_campaign=script_tools&_fallback_redirect=https://desk.bigvu.tv/welcome/init/business-profile).*",
                "info": {
                    "chat_id": "chat_80af7a83-132c-467f-b8f1-fa342a3ab8ba",
                    "agent_name": "bigvu-expert",
                    "user_info": {
                        "id": "user_1_chat_80af7a83-132c-467f-b8f1-fa342a3ab8ba",
                        "utr_num": 1,
                        "DcR_score": 0.4776135054742615
                    },
                    "assistant_info": {
                        "id": "assistant_2_chat_80af7a83-132c-467f-b8f1-fa342a3ab8ba",
                        "utr_num": 2
                    }
                },
                "requires_rewrite": null,
                "models_rewrites": {
                    "prod_rewite": {
                        "text": "can i download a BigVU recorded video to my computer, iPad or iPhone?",
                        "score": null,
                        "optimal": null
                    },
                    "DcR_rewrite": {
                        "text": "can I download a BigVU recorded video to my computer, iPad or iPhone?",
                        "score": null,
                        "optimal": null
                    }
                }
            }
        }
    },
```
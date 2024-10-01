# OneAI Annotation Program Documentation

This repository is designed for administrators. It contains the source code for the program,
allowing you to track annotators' progress on the datasets being annotated,
manage annotation projects (add or delete), and more. Annotators only need the executable (.exe)
file and do not require access to the other files.

## How Annotators Operate the Program

In this section, we will briefly explain how an annotator can operate the program to annotate datasets. Annotators interact with the application via a user-friendly interface, where they can choose datasets, provide annotations, and save their progress.

### Installation

1. Annotators only need to download the executable (`.exe`) file of the program.
2. Double-click the file to launch the program.
3. Enter your `username` in the username field, this username will be an indicator
   where to save you annotations under.
4. Enter `filename` of the dataset you wish to annotate that you got from from an Admin.

#### Important Note About Antivirus Warnings

Sometimes, the operator's antivirus software may mistakenly identify the program as a virus. This happens because `.exe` files usually have a registered developer ID, and this program does not. In such cases, annotators may need to ignore the antivirus warning in order to run the program.

If you encounter this issue, please verify the source of the executable and follow your system's instructions to allow it through the antivirus software. 

# For Administrators

Administrators have full control over managing the annotation projects. This includes adding, removing, and updating datasets, as well as monitoring annotators' progress. Administrators can also retrieve and review all annotations stored in the MongoDB database. 

The source code in this repository provides the necessary tools for administrators to interact with the program, perform data analysis, and manage the overall annotation process. The following sections will guide you through the functionalities available to administrators, including how to retrieve, inspect, and manage annotations.


## Program File Structure

First of all, if you need to familiarize yourself with the program structure, here are the files the program uses for its operation, each with a brief description. Inside each file, you will also find descriptions for every function or class.

- **utils**: Contains various classes used by the main application, including both frontend and backend components. Here you can find classes that manage different parts of the software, like the frame displaying the dialog or the class responsible for MongoDB operations.
  
- **shared_utils**: Helper classes and functions used by `jsonFunctions`, `utils`, and other parts of the program.

- **requiresRewrite**: This code runs when annotators are working on projects where the main goal is to determine if the utterance requires a rewrite.

- **scoringRewrite**: This code is used when annotators need to compare different rewrites and annotate each one with a score and optimal value.

- **jsonFunctions**: Functions to handle JSON files retrieved from MongoDB, used for reading and writing JSON data. Instead of modifying the JSON files directly, the program uses functions from this file to interact with the JSON data.

- **main**: Run this file to start the application.


## The `db.py` File for Administrators

Using the `db.py` file, you can manage and interact with the different datasets that the program uses and that the annotators work on. This includes the ability to delete, add, or update datasets.

Additionally, you can use the `db.py` file to retrieve the annotations made by the annotators for each dataset. This allows you to review their progress and analyze their annotations as needed.

Inside the `db.py` file, you will find several functions, each with a description of its purpose, input, and output, making it easier to understand and use.

We will now go over the main and most important functions.


#### Retrieving Annotations using `retrieve_annotations_by_file_id`

When the annotators use the program to annotate the datasets, their annotations are saved in MongoDB.
To retrieve the annotations from MongoDB for reviewing progress or analyzing their annotations, follow these steps:


1. Import the `db.py` file:

```python
from db import *
```

2. Use the `retrieve_annotations_by_file_id` function. This function takes the desired filename (the dataset you wish to inspect) as input and retrieves all annotations made by the annotators for the specified project. It returns a dictionary, where the keys are the annotators' usernames and the values are the corresponding annotated JSON files.

```python
annotations = retrieve_annotations_by_file_id('your_filename_here')
```

After retrieving the dictionary of annotations, you can inspect and perform various actions with it. For example, to get the list of annotators currently working on the project:

```python
annotators = annotations.keys()
print(annotators)
```

Output:

```python
(['annotator_username1', 'annotator_username2', 'annotator_username3'])
```

If you want to inspect each annotator's annotations, specify the username as a key in the dictionary. The value will be the project's JSON file, which includes the annotator's annotations.

```python
annotator_annotations = annotations['annotator_username1']
print(annotator_annotations)
```


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

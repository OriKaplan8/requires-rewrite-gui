## Getting Started

This section guides you through setting up and starting the Require-rewrite-context-gui program, designed for annotating 'requires rewrite' and 'enough context' fields.

### Installation

Download the executable file (`.exe`) to your computer. Once downloaded, simply double-click the file to launch the program. Upon opening, you will be prompted to enter a name and a `file_id`. 

### Using the Program

To annotate the `asi` dataset:
1. Enter the filename `asi-14-4` in the filename prompt.
2. Provide a username. This username will be associated with your annotations, allowing for personalized data tracking.

### Reviewing Annotations

To view your annotations or those made by other annotators:
- Use the `mongo_data_manager.ipynb` notebook. This notebook contains a function called `retrieve_annotation_by_user_and_file_id`, which you can run with the desired filename and username to retrieve the relevant annotations.

Further details and functions are explained within the notebook itself.

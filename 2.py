# %% [markdown]
# # Initialization of MongoDB Connection
# 
# This section of the code initializes the necessary Python libraries and sets up the connection to a MongoDB database. Below is an explanation of each component:
# 
# ## Libraries Imported
# 
# - **pymongo**: Used to work with MongoDB from Python. This library enables the creation of a client to interact with the database.
# - **datetime**: Provides classes for manipulating dates and times. It's used here to record timestamps when updating or inserting documents.
# - **json**: Supports JSON parsing. This module enables loading and parsing JSON data from files or strings.
# 
# ## Database Connection
# 
# - **Connection String**: A string that specifies the MongoDB server to connect to, including credentials and other connection options.
# - **Client Setup**: The `MongoClient` object is created using the connection string, which facilitates operations like inserting, retrieving, updating, and deleting documents.
# - **Database Selection**: Specifies the database (`require_rewrite_b`) from the MongoDB server to be used for operations.
# 
# This setup is essential for performing any database operations that follow in the subsequent code.
# 

# %%
#initlize eveything
from pymongo import MongoClient #mongo libary for the server
import datetime #for the time
import json #for the json files
connection_string = "mongodb+srv://orik:Ori121322@cluster0.tyiy3mk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" #the connection string, the adress of the server 
client = MongoClient(connection_string)
db = client.require_rewrite_b #the name of the database

# %% [markdown]
# # Database Functions for JSON Data Management
# 
# This document outlines various Python functions designed for managing JSON data in a MongoDB database. These functions enable adding, updating, retrieving, and deleting JSON templates and annotations.
# 
# ## Functions
# 
# ### `add_or_update_json_template_in_db`
# 
# - **Purpose**: Adds or updates a JSON template in the MongoDB collection. These templates serve as the basis for annotations, which users can select and annotate.
# - **Parameters**:
#   - `project_name` (str): Name of the project.
#   - `file_id` (str): ID of the file.
#   - `json_data` (dict): JSON data to be added.
#   - `overwrite` (bool): If true, updates the document if already exists; otherwise, inserts new.
# - **Returns**: None.
# 
# ### `retrieve_json_template_by_file_id`
# 
# - **Purpose**: Retrieves the JSON template based on file ID from the MongoDB collection.
# - **Parameters**:
#   - `file_id` (str): ID of the file.
# - **Returns**: JSON data as a dictionary.
# 
# ### `retrieve_annotations_by_file_id`
# 
# - **Purpose**: Retrieves all annotations for a given file ID. Initially, the JSON data in annotations contains fields set to null to indicate that they have not been annotated.
# - **Parameters**:
#   - `file_id` (str): ID of the file.
# - **Returns**: A dictionary containing annotations, indexed by username. As users interact with the annotation software, fields that are annotated are updated with actual values.
# 
# ### `retrieve_annotation_by_user_and_file_id`
# 
# - **Purpose**: Retrieves the annotated file for a specific user and file ID. The annotations start with null values and are populated with data as the user performs annotations.
# - **Parameters**:
#   - `file_id` (str): ID of the file.
#   - `username` (str): Username of the annotator.
# - **Returns**: JSON data of the annotated file, if found. Fields are initially set to null and updated as the user annotates them.
# 
# ### `delete_json_template_and_annotations_by_file_id`
# 
# - **Purpose**: Deletes a JSON template and all associated annotations based on file ID.
# - **Parameters**:
#   - `file_id` (str): ID of the file.
# - **Returns**: None.
# 
# ### `load_json_from_file`
# 
# - **Purpose**: Loads JSON data from a file.
# - **Parameters**:
#   - `file_path` (str): Path to the JSON file.
# - **Returns**: JSON data as a dictionary.
# 

# %%
def add_or_update_json_template_in_db(project_name, file_id, json_data, overwrite=False):
    """
    Adds a JSON template to the MongoDB collection.

    Parameters:
    - project_name (str): The name of the project.
    - file_id (str): The ID of the file.
    - json_data (dict): The JSON data to be added.
    - overwrite (bool): If True, the document will be updated if it exists. If False, the document will only be inserted if it doesn't exist.

    Returns:
    None
    """
    collection = db.json_batches
    query = {'file_id': file_id}

    if overwrite:
        # Update the document if it exists, or insert if it doesn't
        my_values = {"$set": {'file_id': file_id, 'json_data': json_data, 'project_name': project_name,
                              'annotated': False, 'uploaded': datetime.datetime.now()}}
    else:
        # Only set these fields if the document does not exist and is being inserted
        my_values = {"$setOnInsert": {'file_id': file_id, 'json_data': json_data, 'project_name': project_name,
                                      'annotated': False, 'uploaded': datetime.datetime.now()}}

    update_result = collection.update_one(query, my_values, upsert=True)
    
    if update_result.matched_count > 0:
        print(f"Document with file_id {file_id} updated.")
    elif update_result.upserted_id is not None:
        print(f"New document inserted with id {update_result.upserted_id}.")
    else:
        print("No changes made to the database.")
        
def retrieve_json_template_by_file_id(file_id):
    """
    Retrieves the JSON data from the MongoDB collection based on the specified file ID.

    Args:
        file_id (str): The ID of the file to retrieve the JSON data for.

    Returns:
        dict: The JSON data retrieved from the MongoDB collection.

    Raises:
        None

    """
    collection = db.json_batches
    query = {'file_id': file_id}
    result = collection.find_one(query)
    if result:
        print("Found document:")
        print(result['json_data'])  # Print only the json_data field
        return result['json_data']  # Return only the json_data field
    else:
        print("No document found with the specified project name and file ID.")
        return None

def retrieve_annotations_by_file_id(file_id):
    """
    Retrieves the annotated JSON data from the MongoDB collection based on the specified file ID.

    Args:
        file_id (str): The ID of the file to retrieve the annotated JSON data for.

    Returns:
        dict: The annotated JSON data retrieved from the MongoDB collection.

    Raises:
        None

    """
    collection = db.json_annotations
    query = {'file_id': file_id}
    result = collection.find(query)
    json_data = {}
    if result is not  None:
        for document in result:

            json_data[document["username"]] = document["json_data"]
                
     
        return json_data  # Return only the json_data field
    else:
        print("No document found with the specified project name and file ID.")
        return None
    
def retrieve_annotation_by_user_and_file_id(file_id, username):
    """
    Retrieves the annotated file of a specific annotator from the MongoDB collection.

    Parameters:
    - file_id (str): The ID of the file to retrieve.
    - username (str): The username of the annotator.

    Returns:
    - json_data (dict): The JSON data of the annotated file, if found.
    - None: If no document is found with the specified file ID or username.
    """

    collection = db.json_annotations
    query = {'file_id': file_id}
    result = collection.find_one(query)
    json_data = {}
    if result is not None:
        query = {'file_id': file_id, 'username': username}
        result = collection.find_one(query)
        if result is not None:
            json_data = result["json_data"]
            return json_data  # Return only the json_data field
        else: 
            print("No document found with the specified username.")
            return None
    else:
        print("No document found with the specified file ID.")
        return None
    
def delete_json_template_and_annotations_by_file_id(file_id):
    """
    Deletes a JSON template from the MongoDB collection based on the specified file ID.

    Args:
        file_id (str): The ID of the file to delete.

    Returns:
        None

    Raises:
        None

    """
    collection = db.json_batches
    query = {'file_id': file_id}
    result = collection.delete_one(query)
    if result.deleted_count > 0:
        print(f"Document with file_id {file_id} deleted.")

        collection = db.json_annotations
        query = {'file_id': file_id}
        result = collection.delete_many(query)
        print(f"Deleted {result.deleted_count} annotations for file_id {file_id}.")

    else:
        print("No document found with the specified file ID.")

def load_json_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise Exception(f"Cannot find the json file: {file_path}. is the path correct? is it a json file?") 



# %% [markdown]
# Example of retrieve_annotation_by_user_and_file_id:
#  - returns the annotated json file ori is currently annotating

# %%
retrieve_annotation_by_user_and_file_id("asi-14_4", "ori")



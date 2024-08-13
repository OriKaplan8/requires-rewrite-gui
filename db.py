from pymongo import MongoClient  # mongo libary for the server
import datetime  # for the time
import json  # for the json files
import re


connection_string = "mongodb+srv://ori:CqxF0bLlZoX2OQoD@cluster0.agjlk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # the connection string, the adress of the server
client = MongoClient(connection_string)
db = client.require_rewrite_b  # the name of the database


def add_or_update_json_template_in_db(
    project_name, file_id, json_data, overwrite=False
):
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
    query = {"file_id": file_id}

    if overwrite:
        # Update the document if it exists, or insert if it doesn't
        my_values = {
            "$set": {
                "file_id": file_id,
                "json_data": json_data,
                "project_name": project_name,
                "annotated": False,
                "uploaded": datetime.datetime.now(),
            }
        }
    else:
        # Only set these fields if the document does not exist and is being inserted
        my_values = {
            "$setOnInsert": {
                "file_id": file_id,
                "json_data": json_data,
                "project_name": project_name,
                "annotated": False,
                "uploaded": datetime.datetime.now(),
            }
        }

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
    query = {"file_id": file_id}
    result = collection.find_one(query)
     
    if result: # If a document is found
        if "asi" in re.split(r'[ _\-]', file_id):
            return convert_old_to_new_format(result["json_data"])
        
        return result["json_data"]  # Return only the json_data field
    else:
        print("No document found with the specified project name and file ID.")
        return None
    
def file_exists(file_id):
        collection = db.json_batches
        query = {"file_id": file_id}
        if collection.find_one(query):
            return True
        else:
            return False

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
    if not file_exists(file_id):
        print("No document found with the specified project name and file ID.")
        return None
    
    json_data = {}

    if "asi" in re.split(r'[ _\-]', file_id):
        collection = db.json_annotations
        query = {"file_id": file_id}
        result = collection.find(query)
        json_data = {}
        if result is not None:
            for document in result:
                json_data.update({document["username"]: document["json_data"]})
                print(document["username"])

    collection = db.json_annotations_dialogs
    query = {"file_id": file_id}
    result = collection.find(query)
    template = None
    for result in result:
        if result["username"]  == "test111" and result["dialog_id"] == "QReCC-Train_1354":
            print("here i am") 
            
        if result["username"] in list(json_data.keys()):
            json_data[result["username"]][result["dialog_id"]] = result["dialog_data"]

        else:
            if template is None:
                template = retrieve_json_template_by_file_id(file_id)
            json_data[result["username"]] = template
            json_data[result["username"]][result["dialog_id"]] = result["dialog_data"]
            

    for key, json in json_data.items():
        json_data[key] = convert_old_to_new_format(json)

    return json_data

           
def retrieve_annotation_by_user_and_file_id(file_id, username):
    """
    Retrieve annotations by user and file ID.

    Args:
        file_id (str): The ID of the file.
        username (str): The username of the user.

    Returns:
        dict or None: A dictionary containing the retrieved annotations if found, 
                      None if no annotations were found.
    """

    json_data = None
    found_any = False
    old_version = False
    
    if "asi" in re.split(r'[ _\-]', file_id):
        json_data = retrieve_old_annotations_by_user_and_file_id(file_id, username)
        found_any = True if json_data else False
        old_version = True
    
    if not json_data:
        json_data = retrieve_json_template_by_file_id(file_id)
        if not json_data:
            return None
     
    collection = db.json_annotations_dialogs
    query = {"username": username, "file_id": file_id}
    results = collection.find(query) 

    for result in results:
        json_data[result["dialog_id"]] = result["dialog_data"]
        found_any = True

    if not found_any:
        print("No annotations found with the specified username.")
        return None
    
    if old_version:
        return convert_old_to_new_format(json_data)
    
    else:
        return json_data

def convert_old_to_new_format(old_data):
    """
    Converts old data format to a new format.
    Old data includes the following:
        - asi-14_4
        - asi-23_4

    Args:
        old_data (dict): The old data to be converted.

    Returns:
        dict: The new data in the updated format.
    """
    new_data = {}
    for dialog_key, dialog_data in old_data.items():
        
        if isinstance(dialog_data["dialog"], dict):
            new_data[dialog_key] = dialog_data
            continue # Already in the new format

        new_dialog = {"number_of_turns": 0,
                    "annotator_id": dialog_data["annotator_id"],
                    "dialog": {}}
        
        for index, value in enumerate(dialog_data["dialog"]):
            new_dialog["dialog"][str(index)] = value
            new_dialog["number_of_turns"] += 1

            if index > 0:
                new_dialog["dialog"][str(index)]["requires_rewrite"] = dialog_data[str(index)]["requires_rewrite"]
                new_dialog["dialog"][str(index)]["enough_context"] = dialog_data[str(index)]["enough_context"]

            
        new_data[dialog_key] = new_dialog
        
    return new_data
           
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
    query = {"file_id": file_id}
    result = collection.delete_one(query)
    if result.deleted_count > 0:
        print(f"Document with file_id {file_id} deleted.")

        collection = db.json_annotations
        query = {"file_id": file_id}
        result = collection.delete_many(query)
        print(f"Deleted {result.deleted_count} annotations for file_id {file_id}.")

    else:
        print("No document found with the specified file ID.")

def load_json_from_file(file_path):
    """
    Load JSON data from a file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The JSON data loaded from the file.

    Raises:
        Exception: If the file is not found or if it is not a valid JSON file.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise Exception(
            f"Cannot find the json file: {file_path}. Is the path correct? Is it a JSON file?"
        )

def retrieve_old_annotations_by_user_and_file_id(file_id, username):
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
            return None
    else:
        return None
    



import re
def compare_norm_texts(text1, text2):
    """
    Compare two normalized texts and return True if they are equal, False otherwise.

    Parameters:
    text1 (str): The first text to compare.
    text2 (str): The second text to compare.

    Returns:
    bool: True if the normalized texts are equal, False otherwise.
    """

    def normalize_string(input_string):
        # Remove symbols using regular expression
        normalized_string = re.sub(r"[^\w\s]", "", input_string)

        # Convert to lowercase
        normalized_string = normalized_string.lower()

        # Remove spaces
        normalized_string = normalized_string.replace(" ", "")

        return normalized_string

    if text1 is None and text2 is None:
        raise ValueError("Both text1 and text2 are None")
    elif text1 is None:
        raise ValueError("text1 is None")
    elif text2 is None:
        raise ValueError("text2 is None")

    if normalize_string(text1) == normalize_string(text2):
        return True

    else:
        return False

import json
from collections import defaultdict

def form_data_to_json(form_data):
    """
    Convert form data to JSON format.
    :param form_data: The form data to convert.
    :return: JSON string representation of the form data.
    """
    try:
        # Convert the form data to a dictionary
        print('form_data:', form_data)
        data_dict = {key: value for key, value in form_data.items()}
        
        # Convert the dictionary to a JSON string
        json_data = json.dumps(data_dict)
        ###TODO: save data to database
        with open('form_data.json', 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
        return json_data
    except Exception as e:
        print(f"Error converting form data to JSON: {e}")
        return None
    

def prefix_to_json(prefixes):
    result = defaultdict(set)

    for prefix in prefixes:
        parts = prefix.strip('/').split('/')
        if len(parts) >= 2:
            top_level = parts[0]
            sub_folder = parts[1]
            result[top_level].add(sub_folder)

    return {
        "data_source": {
            k: sorted(v) for k, v in result.items()
        }
    }

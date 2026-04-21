from flask import jsonify


def populate_object(obj, data_dictionary):
    fields = data_dictionary.keys()

    for field in fields:
        try:
            getattr(obj, field)
            setattr(obj, field, data_dictionary[field])

        except AttributeError:
            return jsonify({'message': 'attribute not in obj'})

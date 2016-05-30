import requests
from .datamodel import Category, Endpoint, Parameter, Response, Return, Field, Model


def find_comma(s):
    # Find the first , (not between other <>)
    counter = 0
    for pos, c in enumerate(s):
        if c == '«':
            counter += 1
        if c == '»':
            counter -= 1
        if c == ',' and counter == 0:
            return pos
    return -1


def swagit(user, password, url):
    session = requests.session()
    session.auth = (user, password)

    categories = session.get(url)
    assert categories.status_code >= 200 and categories.status_code < 300, (categories.status_code, categories.content)
    categories = categories.json()

    api_categories = []
    for cat in categories["apis"]:
        print(cat["path"])

        cat_api = session.get(url + cat["path"]).json()

        models = []
        for name, model in cat_api.get("models", {}).items():
            fields = []
            # Collections are in fact lists of objects
            # No need to create an empty shell
            if name.startswith("Collection") or name.startswith("Locale"):
                continue
            for pname, field in model["properties"].items():
                # Transform collections into lists
                if field["type"].startswith("Collection"):
                    field["items"] = {"type": field["type"].replace("Collection«", "")[:-1]}
                    field["type"] = "array"

                if field["type"] == "array":
                    item_type = field.get("items", {}).get("type", "")
                    if item_type.startswith("Entry"):
                        field["type"] = "dict"
                        # Remove Entry<.*> but keep what's between <>
                        item_type = item_type.replace("Entry«", "")[:-1]
                        comma = find_comma(item_type)
                        assert comma >= 0
                        key_type = item_type[:comma]
                        val_type = item_type[comma + 1:]
                        field["items"] = {"type": (key_type, val_type)}
                if field["type"] == "Locale":
                    field["type"] = "str"
                if field.get("items", {}).get("type") == "Locale":
                    field["items"]["type"] = "str"
                fields.append(Field(pname, field["type"], field["required"], field.get("items", {}).get("type"), field.get("enum")))
            models.append(Model(name, fields))

        models = sorted(models, key=lambda m: m.name)

        endpoints = []
        for endpoint in cat_api["apis"]:
            operations = []
            for operation in endpoint["operations"]:
                returns = Return(operation["type"], operation.get("items", {}).get("type"))
                parameters = {}
                for parameter in operation["parameters"]:
                    item_type = parameter["type"]
                    if item_type == "array":
                        item_type = parameter.get("items", {}).get("type")

                    # Swagger add false bodies sometimes...
                    if parameter["paramType"] == "body":
                        if item_type == "Principal":
                            continue
                        if item_type == "User":
                            continue

                    parameters[parameter["name"]] = Parameter(parameter["defaultValue"],
                                                              parameter["description"],
                                                              parameter["name"],
                                                              parameter["paramType"],
                                                              parameter["type"],
                                                              parameter["required"],
                                                              parameter["allowMultiple"],
                                                              parameter.get("items", {}).get("type"),
                                                              parameter.get("enum"))
                parameters = list(parameters.values())

                responses = []
                for response in operation["responseMessages"]:
                    responses.append(Response(response["code"], response["message"]))

                operations.append(Endpoint(endpoint["description"], endpoint["path"], operation["summary"], operation["method"],
                                           parameters, responses, returns))

            endpoints += operations

        cat = Category(cat["description"], endpoints, models)
        api_categories.append(cat)

    return api_categories

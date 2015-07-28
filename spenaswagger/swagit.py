import requests
from .datamodel import Category, Endpoint, Parameter, Response, Return, Field, Model


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
            for pname, field in model["properties"].items():
                fields.append(Field(pname, field["type"], field["required"], field.get("items", {}).get("type")))
            models.append(Model(name, fields))

        models = sorted(models, key=lambda m: m.name)
        available_models = set([m.name for m in models])

        endpoints = []
        for endpoint in cat_api["apis"]:
            operations = []
            for operation in endpoint["operations"]:
                returns = Return(operation["type"], operation.get("items", {}).get("type"))
                parameters = {}
                for parameter in operation["parameters"]:
                    if parameter["paramType"] == "body" and parameter["type"] not in available_models:
                        continue
                    parameters[parameter["name"]] = Parameter(parameter["defaultValue"],
                                                              parameter["description"],
                                                              parameter["name"],
                                                              parameter["paramType"],
                                                              parameter["type"],
                                                              parameter["required"],
                                                              parameter["allowMultiple"],
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

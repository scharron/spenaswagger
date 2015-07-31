from .datamodel import Transformer
from jinja2 import PackageLoader, Environment
import os


def remove_generics(t):
    t = "_".join(t.split("«")).replace("»", "")
    t = t.replace(",", "_")
    return t


def map_type(t):
    type_mapping = {
        "string": "str",
        "object": "object",
        "integer": "int",
        "boolean": "bool",
        "array": "list",
        "number": "float",
    }
    t = remove_generics(t)
    return type_mapping.get(t, t)


class PyTransformer(Transformer):
    def __init__(self):
        super().__init__()

    def transform_category(self, cat):
        return {"name":  ''.join([s.capitalize() for s in cat.name.split(" ")])}

    def transform_model(self, model):
        return {"name": remove_generics(model.name)}

    def transform_fields(self, fields):
        return list(sorted(fields, key=lambda f: 0 if f.required else 1))

    def transform_field(self, field):
        return {"type": map_type(field.type)}

    def transform_parameter(self, parameter):
        return {"type": map_type(parameter.type), "items": map_type(parameter.items or "")}

    def transform_parameters(self, params):
        return list(sorted(params, key=lambda p: 0 if p.required else 1))

    def transform_return(self, return_):
        return {"type": map_type(return_.type), "items": map_type(return_.items or "")}


def gen_py(api_categories):
    transformer = PyTransformer()
    api_categories = transformer.transform(api_categories)

    try:
        os.makedirs("generated")
    except FileExistsError:
        pass

    env = Environment(loader=PackageLoader("spenaswagger", "templates"), trim_blocks=True, lstrip_blocks=True)

    def to_value(arg):
        if type(arg) != str:
            return arg

        if arg == "false":
            return "False"
        elif arg == "true":
            return "True"
        return '"' + arg + '"'

    def as_args(args):
        args = list(sorted(args, key=lambda a: a.name))
        req_args = [a.name for a in args if a.required]
        def_args = [a.name + "=" + (to_value(getattr(a, "default", None)) or "None") for a in args if not a.required]
        return ', '.join(["self"] + req_args + def_args)

    def query_args(parameters):
        args = ['"' + p.name + '": ' + p.name for p in parameters if p.paramType == "query"]
        args = ', '.join(args)
        return "{" + args + "}"

    def body(parameters):
        return [p.name for p in parameters if p.paramType == "body"]

    def errors_dict(errors):
        return {r.code: r.message for r in errors}

    def as_calling_args(parameters):
        return ', '.join([p.name + "=" + p.name for p in parameters])

    def path_to_function(endpoint):
        path = endpoint.path.split("/")
        path = [p for p in path if len(p) > 0]
        path = [p for p in path if p[0] != "{"] + ["by_" + p[1:-1] for p in path if p[0] == "{"]
        path = [endpoint.method.lower()] + path
        return "_".join(path)

    def is_model(type, models):
        return type in [m.name for m in models]

    def needs_enum(models):
        return any([field.enum is not None for model in models for field in model.fields])

    env.filters['as_args'] = as_args
    env.filters['query_args'] = query_args
    env.filters['body'] = body
    env.filters['errors_dict'] = errors_dict
    env.filters['as_calling_args'] = as_calling_args
    env.filters['path_to_function'] = path_to_function
    env.filters['is_model'] = is_model
    env.filters['needs_enum'] = needs_enum

    template = env.get_template("base.py.jinja")
    with open("generated/base.py", "w") as base_file:
        base_file.write(template.render())

    template = env.get_template("api.py.jinja")
    for api in api_categories:
        with open("generated/" + api.name + ".py", "w") as api_file:
            api_file.write(template.render(api=api))

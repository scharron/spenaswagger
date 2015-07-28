from collections import namedtuple


# Swagger Data Model
Category = namedtuple("Category", ["name", "endpoints", "models"])
Endpoint = namedtuple("Endpoint", ["name", "path", "description", "method", "parameters", "responses", "return_"])
Parameter = namedtuple("Parameter", ["default", "description", "name", "paramType", "type", "required", "multiple", "enum"])
Response = namedtuple("Response", ["code", "message"])
Return = namedtuple("Return", ["type", "items"])
Field = namedtuple("Field", ["name", "type", "required", "items"])
Model = namedtuple("Model", ["name", "fields"])


# Patch namedtuple
def h(self):
    return hash((self.name, frozenset(self.fields)))
Model.__hash__ = h
# /Patch


class Transformer:
    def __init__(self):
        pass

    def transform_categories(self, categories):
        return categories

    def transform_category(self, category):
        return

    def transform_endpoints(self, endpoints):
        return endpoints

    def transform_endpoint(self, endpoint):
        return

    def transform_parameters(self, parameters):
        return parameters

    def transform_parameter(self, parameter):
        return

    def transform_return(self, return_):
        return

    def transform_fields(self, fields):
        return fields

    def transform_field(self, field):
        return

    def transform_models(self, models):
        return models

    def transform_model(self, model):
        return

    def transform_responses(self, responses):
        return responses

    def transform_response(self, response):
        return

    def transform(self, categories):
        categories = [self._transform_category(cat) for cat in categories]
        categories = self.transform_categories(categories)
        return categories

    def _transform_category(self, category):
        modified = self.transform_category(category)
        if modified is not None:
            category = category._replace(**modified)

        endpoints = [self._transform_endpoint(e) for e in category.endpoints]
        endpoints = self.transform_endpoints(endpoints)

        models = [self._transform_model(e) for e in category.models]
        models = self.transform_models(models)

        return category._replace(endpoints=endpoints, models=models)

    def _transform_endpoint(self, endpoint):
        modified = self.transform_endpoint(endpoint)
        if modified is not None:
            endpoint = endpoint._replace(**modified)

        parameters = [self._transform_parameter(e) for e in endpoint.parameters]
        parameters = self.transform_parameters(parameters)

        responses = [self._transform_response(e) for e in endpoint.responses]
        responses = self.transform_responses(responses)

        return_ = endpoint.return_
        modified = self.transform_return(return_)
        if modified is not None:
            return_ = return_._replace(**modified)

        return endpoint._replace(parameters=parameters, responses=responses, return_=return_)

    def _transform_parameter(self, parameter):
        modified = self.transform_parameter(parameter)
        if modified is not None:
            parameter = parameter._replace(**modified)

        return parameter

    def _transform_response(self, response):
        modified = self.transform_response(response)
        if modified is not None:
            response = response._replace(**modified)

        return response

    def _transform_model(self, model):
        modified = self.transform_model(model)
        if modified is not None:
            model = model._replace(**modified)

        fields = [self._transform_field(e) for e in model.fields]
        fields = self.transform_fields(fields)

        return model._replace(fields=fields)

    def _transform_field(self, field):
        modified = self.transform_field(field)
        if modified is not None:
            field = field._replace(**modified)

        return field

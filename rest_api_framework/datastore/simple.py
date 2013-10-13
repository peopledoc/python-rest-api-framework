from .base import DataStore
from rest_api_framework import models
from werkzeug.exceptions import NotFound


class PythonListDataStore(DataStore):
    """
    a datastore made of list of dicts
    """

    def __init__(self, ressource_config, model, **options):
        self.data = ressource_config
        super(PythonListDataStore, self).__init__(ressource_config,
                                                  model,
                                                  **options)

    def get(self, identifier):
        """
        return an object matching the uri or None
        """
        for elem in self.data:
            if elem['id'] == identifier:
                return elem
        raise NotFound

    def filter(self, **kwargs):
        data = self.ressource_config
        for k, v in kwargs.iteritems():
            try:
                data = [elem for elem in data if elem[k] == v]
            except KeyError:
                pass
        return data

    def get_list(self, offset=0, count=None, **kwargs):
        """
        return all the objects paginated if needed
        """
        data = self.filter(**kwargs)
        return self.paginate(data, offset=offset, count=count)

    def create(self, data):

        self.validate(data)
        obj = {}
        for k, v in data.iteritems():
            if k in self.model.get_fields():
                obj[k] = v

        for field in self.model.get_fields():
            if isinstance(field, models.PkField):
                self.data.sort(lambda a, b: a[field.name] > b[field.name])
                last = self.data[-1][field.name]
                obj[field.name] = last + 1

        self.data.append(obj)
        return obj["id"]

    def update(self, obj, data):
        """
        Update a single object
        """
        # chek if the object already exists
        self.get(obj['id'])
        # check the fields to be updated
        self.validate_fields(data)
        # update the object
        for k, v in data.iteritems():
            obj[k] = v

        # save it in the datastore
        self.data[obj['id']] = obj
        # return the object
        return obj

    def delete(self, identifier):
        obj = self.get(identifier)
        self.data.remove(obj)
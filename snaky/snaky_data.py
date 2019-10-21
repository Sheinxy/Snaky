import json
import os

class SnakyData:
    '''
        This is a small 'database manager-like' used to store data with this bot.
        The root is the location of the database, it is a string corresponding to a
        directory or file path.
        Data is stored inside .json files.
        A Ref is like a nested database.
    '''

    def __init__(self, root):
        self.root = root
        self.create_data()

    def create_data(self, path="/"):
        '''
            Creates a database folder.
            The path is added to the root.
            This will not create any file.
        '''
        total_path = self.root + \
            path if path == "" or path[0] == '/' else self.root + '/' + path
        if not os.path.isdir(os.path.dirname(total_path)):
            os.makedirs(os.path.dirname(total_path))


    def get_data(self, path="", ifEmpty={}):
        '''
            Retrieves data from a .json file.
            The path is added to the root.
            The total path must be a .json file.
            The ifEmpty value is what will be written and return
            if the file is empty or doesn't exist.
        '''
        self.create_data(path=path)
        total_path = self.root + \
            path if path == "" or path[0] == '/'  else self.root + '/' + path
        if not os.path.exists(total_path):
            with open(total_path, 'w') as data_file:
                json.dump(ifEmpty, data_file, indent=4)
        with open(total_path) as data_file:
            data = json.load(data_file)
        return data

    def set_data(self, key, value, path=""):
        '''
            Sets data to a .json file.
            The key must be a string.
            The value can be anything that can be stored to a json file.
            The path is added to the root.
            The total path must be a .json file.
        '''
        self.create_data(path=path)
        total_path = self.root + \
            path if path == "" or path[0] == '/'  else self.root + '/' + path

        data = self.get_data(path)
        data[key] = value

        with open(total_path, 'w') as data_file:
            json.dump(data, data_file, indent=4)

    def del_data(self, key, path=""):
        '''
            Removes data to a .json file.
            The key must be a string.
            The path is added to the root.
            The total path must be a .json file.
        '''
        self.create_data(path=path)
        total_path = self.root + \
            path if path == "" or path[0] == '/'  else self.root + '/' + path

        data = self.get_data(path)
        del data[key]

        with open(total_path, 'w') as data_file:
            json.dump(data, data_file, indent=4)

    def push_data(self, value, path=""):
        '''
            Appends data to a .json file.
            Use this when the .json only contains an array.
            The value can be anything that can be stored to a json file.
            The path is added to the root.
            The total path must be a .json file.
        '''
        self.create_data(path=path)
        total_path = self.root + \
            path if path == "" or path[0] == '/'  else self.root + '/' + path

        data = self.get_data(path, [])
        data.append(value)

        with open(total_path, 'w') as data_file:
            json.dump(data, data_file, indent=4)

    def rem_data(self, value, once=True, path=""):
        '''
            Removes value from a .json file.
            Use this when the .json only contains an array.
            The value can be anything that can be stored to a json file.
            By default, only remove the first instance of the value
            To remove all instances, set once to False.
            The path is added to the root.
            The total path must be a .json file.
        '''
        self.create_data(path=path)
        total_path = self.root + \
            path if path == "" or path[0] == '/'  else self.root + '/' + path

        data = self.get_data(path, [])

        while value in data:
            data.remove(value)
            if once:
                break

        with open(total_path, 'w') as data_file:
            json.dump(data, data_file, indent=4)

    def replace_data(self, new_data, path=""):
        '''
            Replaces all the data inside a .json file by some new data
        '''
        self.create_data(path=path)
        total_path = self.root + \
            path if path == "" or path[0] == '/'  else self.root + '/' + path

        with open(total_path, 'w') as data_file:
            json.dump(new_data, data_file, indent=4)

    def get_ref(self, path):
        '''
            Returns a Ref from a specified path.
            The path is added to the root.
            A Ref is like a nested database.

            Eg: 
                data
                |-  subdata1
                    |- data.json

                SnakyData("data").get_ref("subdata1") is the same as SnakyData("data/subdata1")
        '''
        total_path = self.root + \
            path if path == "" or path[0] == '/'  else self.root + '/' + path

        return SnakyData(total_path)

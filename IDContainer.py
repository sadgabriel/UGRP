import SpaceData

class IDContainer:
    def __init__(self) -> None:
        self.container = {}
        self.data = {}

        return
    
    def __setitem__(self, key, value):

        self.container[key] = value
        
        return
    
    def __getitem__(self, key):

        return self.container[key]
    
    def pop(self, key):

        return self.container.pop(key)
    
    def strize(self):

        result = str(self.container)
        result.replace('{', '(')
        result.replace('}', ')')

        return result
    
    def set_data(self, key, data):
        """
        arg
            key: str
            data: tuple

        return
            None
        """
        self.data[key] = SpaceData.SpaceData(data)

        return
    
    def get_data(self, key):
        
        return self.data[key]
    
if __name__ == '__main__':
    idcontainer = IDContainer()
    idcontainer['dragon'] = 1
    idcontainer['warrior'] = 2
    idcontainer['rock'] = 3
    print(idcontainer['dragon'])
    print(idcontainer.container)
class IDContainer:
    def __init__(self) -> None:
        self.container = {}

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
    
if __name__ == '__main__':
    idcontainer = IDContainer()
    idcontainer['dragon'] = 1
    idcontainer['warrior'] = 2
    idcontainer['rock'] = 3
    print(idcontainer['dragon'])
    print(idcontainer.container)
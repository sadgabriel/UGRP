class SpaceData:
    def __init__(self, data_tuple) -> None:
        """
        args
            data_tuple: (move_point)
        
        return
            None
        """

        self.data = {
            'move point': data_tuple[0]
        }

        return
    
if __name__ == '__main__':
    spacedata = SpaceData(5)
    print(spacedata.data)
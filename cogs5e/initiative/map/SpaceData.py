class SpaceData:
    def __init__(self, data_tuple) -> None:
        """
        args
            data_tuple: (hp, movement_point, shooting_range)
        
        return
            None
        """

        self.data = {
            'hp': data_tuple[0],
            'movement point': data_tuple[1],
            'shooting range': data_tuple[2]
        }

        # debuging
        print("spacedata was created.")
        print(self.data)

        return
    
if __name__ == '__main__':
    spacedata = SpaceData(5)
    print(spacedata.data)
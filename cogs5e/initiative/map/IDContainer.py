import SpaceData


class IDContainer:
    def __init__(self) -> None:
        self.container = {}
        self.data = {}

        return

    def __setitem__(self, name: str, id: int) -> None:

        self.container[name] = id

        return

    def __getitem__(self, name: str) -> int:

        return self.container[name]

    def pop(self, name: str) -> int:

        return self.container.pop(name)

    def strize(self) -> str:
        """
        Convert {hp, movement point, shooting range}
        into (hp, movement point, shooting range)
        for AI prompting.
        """

        result = str(self.container)
        result.replace("{", "(")
        result.replace("}", ")")

        return result

    def set_data(self, id: int, data: tuple) -> None:
        """
        arg
            id: int
            data: tuple
        """
        self.data[id] = SpaceData.SpaceData(data)

        return

    def get_data(self, id: int):

        return self.data[id]


if __name__ == "__main__":
    idcontainer = IDContainer()
    idcontainer["dragon"] = 1
    idcontainer["warrior"] = 2
    idcontainer["rock"] = 3
    print(idcontainer["dragon"])
    print(idcontainer.container)

import json

WEIGHTED_LIST_FILENAME = "manual/weighted_list.json"

class Weighted_List:

    def __init__(self):
        self.weighted_list = self.read_list()

    def read_list(self):
        self.weighted_list = []
        with open(WEIGHTED_LIST_FILENAME, "r") as f:
            self.weighted_list = json.load(f)

    def write_list(self):
        with open(WEIGHTED_LIST_FILENAME, "w") as f:
            json.dump(self.weighted_list, f, indent=2)

    def compare_list(self, list: list):
        self.read_list()

        for name in list:
            found = False
            for weighted_name in self.weighted_list["list"]:
                if name == weighted_name:
                    found = True
            if not found:
                self.weighted_list["list"].append(name)

            self.write_list()

    def get_list(self):
        self.read_list()
        return self.weighted_list["list"]
    

if __name__ == "__main__":
    weighted_list = Weighted_List()

    weighted_list.read_list()
    print(weighted_list.get_list())
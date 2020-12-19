import json

# a handler for managing json files as config
class ConfigHandler():
    def __init__(self, path):
        self.path_to_config = path
        self.autosave = True
        self.reload()

    
    def reload(self):
        with open(self.path_to_config, 'r') as f:
            try:
                self.json_unparsed = json.load(f)
            except:
                print("[ERROR] could not read {}".format(self.path_to_config))
                sys.exit()

    def get(self, topic, option=""):
        if not option == "":
            return self.json_unparsed[topic][option]
        else:
            return self.json_unparsed[topic]

    def set(self, topic, option, value=""):
        if not value == "":
            self.json_unparsed[str(topic)][str(option)] = value
        else:
            self.json_unparsed[str(topic)] = option
        if self.autosave(): self.save()

    def save(self,):
        with open(self.path_to_config, 'w') as f:
            json.dump(self.json_unparsed, f, indent=4)
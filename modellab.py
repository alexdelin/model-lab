import os
import sys
import json
import pickle


class ModelLabEnv(object):
    """docstring for ModelLabEnv"""

    def __init__(self, config_file='~/.model-lab.json'):

        self.env_config = self.get_env_config(config_file)
        self.data_dir = self.get_data_dir()
        self.cache = {
            "models": {},
            "implementations": {}
        }

    # ----------Environment----------
    def get_env_config(self, config_location='~/.model-lab.json'):

        if '~' in config_location:
            config_location = os.path.expanduser(config_location)

        with open(config_location, 'r') as env_config_file:
            env_config = json.load(env_config_file)

        return env_config

    def get_data_dir(self):

        data_dir = self.env_config.get('data-dir')
        if data_dir[-1] != '/':
            data_dir += '/'

        return data_dir

    # ----------Training----------
    def list_training(self):

        training_dir = self.data_dir + 'training'
        return os.listdir(training_dir)

    def create_training(self, training_name, training_data=[]):

        relative_training_path = 'training/{name}/{name}_training.json'.format(
                                    name=training_name)
        full_training_path = self.data_dir + relative_training_path

        if os.path.exists(full_training_path):
            raise ValueError('Training to create already exists')

        os.makedirs(os.path.dirname(full_training_path))

        with open(full_training_path, 'r') as training_file:
            json.dump(training_data, training_file)

    def get_training(self, training_name):

        relative_training_path = 'training/{name}/{name}_training.json'.format(
                                    name=training_name)
        full_training_path = self.data_dir + relative_training_path

        with open(full_training_path, 'r') as training_file:
            training_data = json.load(training_file)

        return training_data

    def write_training(self, training_name, training_data):

        relative_training_path = 'training/{name}/{name}_training.json'.format(
                                    name=training_name)
        full_training_path = self.data_dir + relative_training_path

        with open(full_training_path, 'w') as training_file:
            json.dump(training_data, training_file)

    def add_to_training(self, training_name, new_examples):

        training = self.get_training(training_name)

        for new_example in new_examples:
            training.append(new_example)

        self.write_training(training_name, training)

    def deduplicate_training(self, training_name):

        training_contents = self.get_training(training_name)

        unzipped_training = {}
        for example in training_contents:
            unzipped_training[example.get('text')] = example.get('label')

        new_training = []
        for training_text, training_label in unzipped_training.iteritems():
            new_training.append({
                    "text": training_text,
                    "label": training_label
                })

        self.write_training(training_name, new_training)

    # ----------Models----------
    def list_models(self):

        model_dir = self.data_dir + 'models'
        return os.listdir(model_dir)

    def load_model(self, model_name):

        # Early Exit
        if self.cache.get('models', {}).get(model_name):
            raise ValueError('Model is already loaded!')

        relative_model_path = 'models/{name}/model.py'.format(name=model_name)
        full_model_path = self.data_dir + relative_model_path
        full_model_dir = os.path.dirname(full_model_path)

        sys.path.append(full_model_dir)
        from model import Model

        self.cache.setdefault('models', {})
        self.cache['models'][model_name] = Model()

        sys.path.remove(full_model_dir)

    def unload_model(self, model_name):

        if self.cache['models'].get(model_name):
            del self.cache['models'][model_name]
        else:
            raise ValueError('Selected model is currently not loaded')

    def train_model(self, model_name, training_set):

        if not self.cache['models'].get(model_name):
            raise ValueError('Selected Model is currently not loaded')

        self.cache['models'][model_name].train(training_set)

    def evaluate_model(self, model_name, text):

        if not self.cache['models'].get(model_name):
            raise ValueError('Selected Model is currently not loaded')

        label = self.cache['models'][model_name].evaluate(text)
        return label

    # ----------Implementations----------
    def list_implementations(self):

        model_dir = self.data_dir + 'models'
        return os.listdir(model_dir)

    def create_implementation(self, model_name, training_name,
                              implementation_name):

        pass

    def load_implementation(self, implementation_name):

        # Early Exit
        if self.cache.get('implementations', {}).get(implementation_name):
            raise ValueError('Implementation is already loaded!')

        relative_implementation_path = 'implementations/{name}/'\
                                       'implementation.pickle'.format(
                                            name=implementation_name)
        full_implementation_path = self.data_dir + relative_implementation_path

        with open(full_implementation_path, 'r') as implementation_file:
            loaded_implementation = pickle.load(implementation_file)

        self.cache['implementations'][implementation_name] = loaded_implementation

    def save_implementation(self, implementation_name):
        pass

    def unload_implementation(self, implementation_name):

        if self.cache['implementations'].get(implementation_name):
            del self.cache['implementations'][implementation_name]
        else:
            raise ValueError('Selected implementation is currently not loaded')

    def evaluate_implementation(self, implementation_name, text):
        pass

    # ----------Corpora----------
    def list_corpora(self):
        pass

    def get_corpus(self, corpus_name):
        return None

import pickle



def read_pickle(file):
    with open(file, 'rb') as f:
        return pickle.load(f)


def write_pickle(obj, file):
    with open(file, 'wb') as f:
        pickle.dump(obj, f)

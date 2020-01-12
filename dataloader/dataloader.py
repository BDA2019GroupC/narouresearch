from narouresearch.utils.io_util import get_all_path, get_path_by_length
import random

class DataLoader:
    def __init__(self, path, validation_split=0.0, seed=0, extention=[], exception=[], strip_one=False, shuffle=False):
        self.path = path
        self.validation_split = validation_split
        self.extention = extention
        self.exception = exception
        self.seed = seed
        self.strip_one = strip_one
        self.shuffle = shuffle

    def get_generator(self, mode="training"):
        random.seed(self.seed)
        if mode not in ["training", "validation"]: 
            raise Exception("mode must be training or validation.")
        for path in get_all_path(self.path, self.extention, self.exception, shuffle=self.shuffle):
            with open(path) as f:
                if self.strip_one: f.readline()
                for line in f:
                    rand = random.random()
                    if mode == "training" and rand < self.validation_split:
                        continue

                    if mode == "validation" and rand >= self.validation_split:
                        continue

                    yield path, line.rstrip()

class LengthDataLoader(DataLoader):
    def get_generator(self, length, mode="training"):
        random.seed(self.seed)
        if mode not in ["training", "validation"]: 
            raise Exception("mode must be \"training\" or \"validation\".")
        for path in get_path_by_length(self.path, length, self.extention, self.exception, shuffle=self.shuffle):
            with open(path) as f:
                if self.strip_one: f.readline()
                for line in f:
                    rand = random.random()
                    if mode == "training" and rand < self.validation_split:
                        continue

                    if mode == "validation" and rand >= self.validation_split:
                        continue

                    yield path, line.rstrip()

class LengthDataLoaderMultiDomain:
    def __init__(self, domainVolume, paths, validation_split=0.0, seed=0, extention=[], exception=[], strip_ones=(False,False), shuffle=False):
        if len(paths) != domainVolume: raise Exception("paths length must be the same value of domainVolume")
        if len(strip_ones) != domainVolume: raise Exception("strip_ones length must be the same value of domainVolume")
        self.LDLs = [LengthDataLoader(paths[i],validation_split,seed,extention,exception,strip_ones[i],shuffle) for i in range(domainVolume)]
        self.domainVolume = domainVolume

    def get_generator(self, length, mode="training"):
        if mode not in ["training", "validation"]: 
            raise Exception("mode must be \"training\" or \"validation\".")

        generators = [self.LDLs[i].get_generator(length,mode) for i in range(self.domainVolume)]
        existFlag = [True for _ in range(self.domainVolume)]
        while sum(existFlag) > 0:
            for i in range(self.domainVolume):
                if random.random() < 1/self.domainVolume:
                    try:
                        yield generators[i].__next__()
                    except StopIteration: existFlag[i] = False

def BatchDataLoaderWrapper(generator, max_batch_size):
    while True:
        ret_list = []
        for i in range(max_batch_size):
            try:
                ret_list.append(generator.__next__())
            except StopIteration:
                break
        if len(ret_list) == 0: break
        yield ret_list
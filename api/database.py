import pickle

from redis import Redis
import redis

class RedisShelve(Redis):
    def __init__(self, shelve_name, pickle_protocol=-1, host="localhost", db=0):
        super().__init__(host=host, db=db)
        self.shelve_name = shelve_name
        self.pickle_protocol = pickle_protocol

    # def save(self):
    #     self.bgsave()

    def __getitem__(self, key):
        return pickle.loads(self.get(self._get_redis_key(key)))

    def __setitem__(self, key, value):
        pickled_value = pickle.dumps(value, protocol=self.pickle_protocol)
        self.set(self._get_redis_key(key), pickled_value)

    def __delitem__(self, key):
        self.delete(self._get_redis_key(key))

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def keys(self):
        return [str(el).replace(self._get_redis_key(""), "")[2:-1] for el in super().keys()]

    def __contains__(self, key):
        return key in self.keys()

    def _get_redis_key(self, key):
        return "shelve_{}_key_{}".format(self.shelve_name, key)

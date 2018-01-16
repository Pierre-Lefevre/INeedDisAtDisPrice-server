import hashlib
hash_object = hashlib.new('DSA')
name = 'PC Portable Lenovo 320-17IKB 80XM00CDFR 17.3"'
hash_object.update(name.encode('utf-8') )
print(hash_object.hexdigest())
def listify(config, key):
    return config.get(key, '').split()

def process_config_file(config):
    config = config['config']

    if config.get('bidirect', False) and config.get('strict', False):
        raise ValueError('Bidirectional and strict modes can not be applied at once')

    return config

def convert_bytes(size):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.2f %s" % (size, x)
        size /= 1024.0

    return size

def print_(message):
    print(message, end="\r")
    print(" "*len(message), end="\r")
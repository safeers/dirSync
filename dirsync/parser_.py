import argparse
import configparser

from dirsync.utils import listify, process_config_file


def parse_args():
    try:
        config = configparser.ConfigParser()
        config.read('config.txt')
        config = process_config_file(config)
    except:
        config = {}


    parser = argparse.ArgumentParser(description='This program syncs/copies files between two folders')

    parser.add_argument('src', help='Source Folder')
    parser.add_argument('dest', help='Destination Folder')

    parser.add_argument('--max_size', default=config.get('max_size', float('inf')))
    parser.add_argument('--min_size', default=config.get('min_size', 0))

    parser.add_argument('--newer_than', 
                        default=config.get('newer_than', '1/1/1970'), 
                        help='files modified after the date in (format = dd/mm/yyyy)')
    parser.add_argument('--older_than', 
                        default=config.get('older_than', '1/1/2050'),
                        help='files modified after the date in (format = dd/mm/yyyy)')
                        


    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-s', '--strict', 
                        action='store_true',
                        help='deletes files at destination that is absent in source', 
                        default=config.get('strict', False))

    mode.add_argument('-b', '--bidirect', 
                        action='store_true',
                        help='syncs two folder bidirectionally',
                        default=config.get('bidirect', False))


    ext = parser.add_mutually_exclusive_group()
    ext.add_argument('--exc_ext', nargs='*', 
                        help='extensions that should be excluded', 
                        default=listify(config, 'exc_ext'))

    ext.add_argument('--inc_ext', nargs='+', 
                        help='extensions that should be included', 
                        default=listify(config, 'inc_ext'))


    dirs = parser.add_mutually_exclusive_group()
    dirs.add_argument('--exc_dir', nargs='+', 
                        help='directories that should be excluded, absolute unix like paths', 
                        default=listify(config, 'exc_dirs'))

    dirs.add_argument('--inc_dir', nargs='+', 
                        help='directories that should be included, absolute unix like paths', 
                        default=listify(config, 'exc_dirs'))

    return parser.parse_args()

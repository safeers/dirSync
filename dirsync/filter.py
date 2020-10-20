import os
from datetime import datetime


class Filter:
    def __init__(self, args):
        self._max_size = float(args.max_size)
        self._min_size = float(args.min_size)
        if self._max_size < self._min_size:
            raise ValueError("Filter: max size is less than min size")

        self._newer_than = datetime.strptime(args.newer_than, "%d/%m/%Y")
        self._older_than = datetime.strptime(args.older_than, "%d/%m/%Y")
        if self._newer_than > self._older_than:
            raise ValueError("Filter: newerthan > olderthan")

        self._exc_dir = set(args.exc_dir) 
        self._inc_dir = set(args.inc_dir)
        if self._exc_dir and self._inc_dir:
            raise ValueError("exc_dir and inc_dir can't be used at once")

        self._exc_ext = set(args.exc_ext)
        self._inc_ext = set(args.inc_ext)
        if self._exc_ext and self._inc_ext:
            raise ValueError("exc_ext and inc_ext can't be used at once")



    def is_ok(self, path, src):
        return self._is_ok_size(path) and \
            self._is_ok_ext(path) and \
            self._is_ok_dir(path, src) and \
            self._is_ok_date(path)



    def _is_ok_size(self, path):
        bytes_to_MB = lambda bytes: bytes/1048576
        size = os.path.getsize(path)
        size = bytes_to_MB(size)
        if self._min_size <= size <= self._max_size:
            return True
        return False

    def _is_ok_date(self, path):
        mtime = os.path.getmtime(path)    
        if self._newer_than <= datetime.utcfromtimestamp(mtime) <= self._older_than:
            return True
        return False

    def _is_ok_ext(self, path):
        ext = os.path.splitext(path)[-1]
        if self._exc_ext:
            return ext not in self._exc_ext
        if self._inc_ext:
            return ext in self._inc_ext
        return True

    def _is_ok_dir(self, path, src):
        if not src: return True
        if self._exc_dir:
            for dir_ in self._exc_dir:
                abs_dir = os.path.realpath(dir_)
                if os.path.commonpath([abs_dir, path]) == abs_dir:
                    return False
            return True
        if self._inc_dir:
            for dir_ in self._inc_dir:
                abs_dir = os.path.realpath(dir_)
                if os.path.commonpath([abs_dir, path]) == abs_dir:
                    return True
            return False
        return True

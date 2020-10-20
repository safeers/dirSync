import os
import shutil
import sys

import send2trash

from dirsync.filter import Filter
from dirsync.utils import convert_bytes, print_


class Syncer:
    def __init__(self, args):
        self.src = os.path.abspath(args.src)
        self.dest = os.path.abspath(args.dest)
        self.mode = self._get_mode(args)
        self.filter = Filter(args)


    def _get_mode(self, args):
        if args.bidirect: return 'bidirect'
        if args.strict: return 'strict'
        return 'default'
    
    def _load_files(self, dir, src=True):
        if not os.path.isdir(dir) and src:
            raise NotADirectoryError(dir)

        files = {}
        for root, _, filelist in os.walk(dir):
            for file in filelist:
                path = os.path.join(root,file)
                size = os.path.getsize(path)
                if self.filter.is_ok(path, src):
                    files[(size, file)] = path
        return files

    def _get_diff(self):
        self.src_files = self._load_files(self.src, src=True)
        self.dest_files = self._load_files(self.dest, src=False)

        src_set, dest_set = self.src_files.keys(), self.dest_files.keys()
        return src_set - dest_set, dest_set - src_set

    def get_relpath(self, src_path, reverse=False):
        src, dest = self.src, self.dest
        if reverse: src, dest = self.dest, self.src
        

        rel_dest = os.path.relpath(src_path, src)
        rel_dest = os.path.dirname(rel_dest)
        abs_dest_path = os.path.join(dest, rel_dest)
        return abs_dest_path

    def _copy(self, src_path, abs_dest_path):
        os.makedirs(abs_dest_path, exist_ok=True)

        name = os.path.basename(src_path)
        tot_size = convert_bytes(self.tot_size)
        copied_vol = convert_bytes(self.copied_vol)

        message = f"copying {name} ...  {self.copied} / {self.file_count}   {copied_vol} / {tot_size}"
        print_(message)
        shutil.copy2(src_path, abs_dest_path)
        self.copied += 1
        self.copied_vol += os.path.getsize(src_path)


    def _init_stat(self, src_diff, dest_diff):
        self.file_count = len(src_diff)
        self.tot_size = sum([key[0] for key in src_diff])

        if self.mode == "bidirect":
            self.file_count += len(dest_diff)
            self.tot_size += sum([key[0] for key in dest_diff])    
        size_std = convert_bytes(self.tot_size)
        print(f"{size_std}  ({self.file_count}) file(s).")
        
    def _run_default(self, src_diff):
        self.copied= 0
        self.copied_vol = 0
        for file_key in src_diff:
            src_path = self.src_files[file_key]
            abs_dest_path = self.get_relpath(src_path)
            self._copy(src_path, abs_dest_path)
        
    def _run_bidirect(self, dest_diff):
        if self.mode != "bidirect":
            return
        for file_key in dest_diff:
            src_path = self.dest_files[file_key]
            abs_dest_path = self.get_relpath(src_path, reverse=True)
            self._copy(src_path, abs_dest_path)
    
    def _run_strict(self, dest_diff):
        if self.mode != "strict":
            return
        for file_key in dest_diff:
            src_path = self.dest_files[file_key]
            send2trash.send2trash(src_path)
            

    def run(self):
        src_diff, dest_diff = self._get_diff()
        self._init_stat(src_diff, dest_diff)
        self._run_default(src_diff)
        self._run_bidirect(dest_diff)
        self._run_strict(dest_diff)
        sys.stdout.write("Process Completed. All Files copied")



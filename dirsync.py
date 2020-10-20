from dirsync import parser_, syncer

if __name__ == "__main__":

    args = parser_.parse_args()
    syncer = syncer.Syncer(args)
    
    syncer.run()

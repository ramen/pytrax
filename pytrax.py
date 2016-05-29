from pytrax import impulsetracker

if __name__ == "__main__":
    import sys
    import pprint
    if len(sys.argv) > 1:
        info = impulsetracker.parse_file(sys.argv[1], with_samples=True, with_instruments=True, with_patterns=True)
        instruments = info.pop("instruments", None)
        samples = info.pop("samples", None)
        patterns = info.pop("patterns", None)
        
        for i in info:
            print i, "=>", info[i]
        print
        if instruments:
            print len(instruments), "instruments"
        if samples:
            print len(samples), "samples"
        if patterns:
            print len(patterns), "patterns"
    else:
        print "usage:", sys.argv[0], "FILE.it"


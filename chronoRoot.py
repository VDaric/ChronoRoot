from graph.ChronoRoot import ChronoRootAnalyzer
import argparse

if __name__ == "__main__":
    conf = {}
    file = exec(open('config.conf').read(), conf)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--savepath', type=str, help='Output directory', nargs="?")
    parser.add_argument('--imgpath', type=str, help='Input directory', nargs="?")
    parser.add_argument('--segpath', type=str, help='Output directory', nargs="?")

    args = parser.parse_args()

    if not args.savepath:
        pass
    else:
        conf['Project'] = args.savepath

    if not args.imgpath:
        pass
    else:
        conf['Path'] = args.imgpath

    if not args.segpath:
        pass
    else:
        conf['SegPath'] = args.path

    ChronoRhizo(conf)

import sys


def main():
    args = sys.argv[1:]
    count = len(args)
    print(count)
    return 0


def report():
    args = sys.argv[1:]
    count = len(args)
    print(count)


if __name__ == "__main__":
    sys.exit(main())

from sys import argv

def main() -> None:
    _, s_tape, s_left = tuple(argv)
    tape = bin(int(s_tape))[:2:-1]
    left = int(s_left)

    print(tape[:left] + "[" + tape[left] + "]" + tape[left + 1:])

if __name__ == "__main__":
    main()
from sys import stdin

def main() -> None:
    
    guess = 40
    for row in stdin.read().replace("\n-1\n", "/").replace("\n", ",").replace("/", "\n").splitlines():
        state, s_location, s_tape, s_left = tuple(row.split(","))
        left = int(s_left)
        location = len(bin(int(s_location))) - 3 - left + guess
        tape = bin(int(s_tape))[:1:-1].zfill(left + 1)

        thing = tape[:left] + "[" + tape[left] + "]" + tape[left + 1:]
        thing = thing.strip("0")
        thing = " " * (guess - thing.index("[")) + thing
        thing = thing.replace("[", "").replace("]", "")
        thing = " " + " ".join(thing)
        thing = thing.ljust(location * 2 + 4)
        l = list(thing)
        l[2 * location] = "<"
        l[2 * location + 2] = ">"
        thing = "".join(l).replace("0", " ")
        thing = str( int(state) + 1) + ": " + thing
        print(thing)

if __name__ == "__main__":
    main()
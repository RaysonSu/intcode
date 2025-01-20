from __future__ import annotations
from collections import defaultdict
from sys import argv


class Intcode:
    PARAMETER_TYPES = {
        1: (1, 1, 0),
        2: (1, 1, 0),
        3: (0, ),
        4: (1, ),
        5: (1, 1),
        6: (1, 1),
        7: (1, 1, 0),
        8: (1, 1, 0),
        9: (1, )
    }

    def __init__(self, program: list[int]) -> None:
        self.program: defaultdict[int, int] = defaultdict(int)
        for key, value in enumerate(program):
            self.program[key] = value

        self.outputs: list[int] = []
        self.instruction_pointer = 0
        self.relative_base = 0

    def read_input(self, input_value: int) -> bool:
        input_read = False

        while self.program[self.instruction_pointer] != 99:
            prev_index = self.instruction_pointer
            
            opcode_unpared = self.program[self.instruction_pointer]
            opcode = opcode_unpared % 100

            try:
                parameter_type = self.PARAMETER_TYPES[opcode]
            except:
                print(f"Invalid opcode: {opcode}")
                print(f"Memory addr: {self.instruction_pointer}")
                print(f"Local memory: {self.get_memory_range(self.instruction_pointer, 4)}")

            parameter_count = len(self.PARAMETER_TYPES[opcode])

            modes = tuple([
                int(str(opcode_unpared)[
                    :-2].zfill(parameter_count)[::-1][parameter])
                for parameter in range(parameter_count)
            ])

            parameters_unparsed = [
                self.program[self.instruction_pointer + i + 1]
                for i in range(parameter_count)
            ]

            params = [0 for _ in parameter_type]
            for i, param_type in enumerate(parameter_type):
                if param_type == 0:
                    if modes[i] == 0:
                        params[i] = parameters_unparsed[i]
                    elif modes[i] == 2:
                        params[i] = parameters_unparsed[i] + self.relative_base
                    else:
                        raise ValueError("Oh crap!")
                    continue

                if param_type == 1:
                    if modes[i] == 0:
                        params[i] = self.program[parameters_unparsed[i]]
                    elif modes[i] == 1:
                        params[i] = parameters_unparsed[i]
                    elif modes[i] == 2:
                        params[i] = self.program[parameters_unparsed[i] +
                                                 self.relative_base]
                    else:
                        raise ValueError("Oh crap!")
                    continue

                raise ValueError("Oh crap!")
            
            # if opcode == 4:
            #     input(f"{self.instruction_pointer} [{self.relative_base}]: {opcode} {params}")

            if opcode == 1:
                self.program[params[2]] = params[0] + params[1]
            elif opcode == 2:
                self.program[params[2]] = params[0] * params[1]
            elif opcode == 3:
                if input_read:
                    return False

                self.program[params[0]] = input_value
                input_read = True
            elif opcode == 4:
                if params[0] > 255:
                    pass
                self.outputs.append(params[0])
            elif opcode == 5:
                if params[0]:
                    self.instruction_pointer = params[1]
            elif opcode == 6:
                if not params[0]:
                    self.instruction_pointer = params[1]
            elif opcode == 7:
                self.program[params[2]] = int(params[0] < params[1])
            elif opcode == 8:
                self.program[params[2]] = int(params[0] == params[1])
            elif opcode == 9:
                self.relative_base += params[0]
            else:
                raise ValueError("Oh crap!")

            if self.instruction_pointer == prev_index:
                self.instruction_pointer += parameter_count + 1
        return True

    def read_output(self) -> int:
        return self.outputs.pop(0)

    def read_output_all(self) -> list[int]:
        ret = self.outputs.copy()
        self.outputs = []
        return ret

    def read_memory(self, index: int) -> int:
        return self.program[index]

    def set_memory(self, index: int, value: int) -> None:
        self.program[index] = value
    
    def get_memory_range(self, index: int, size: int) -> str:
        ret = ""
        ret += ", ".join([str(self.read_memory(index - i)) for i in range(1, size + 1)])
        ret += f", [{self.read_memory(index)}], "
        ret += ", ".join([str(self.read_memory(index + i)) for i in range(1, size + 1)])
        return ret

    def copy(self) -> Intcode:
        ret = Intcode([])
        ret.program = self.program.copy()
        ret.instruction_pointer = self.instruction_pointer
        ret.relative_base = self.relative_base
        ret.outputs = self.outputs.copy()

        return ret


def main() -> None:
    modifiers: list[str]

    if len(argv) < 3:
        print(f"Too few arguments. (expected 2-3, got {len(argv) - 1})")
        return
    elif len(argv) > 4:
        print(f"Too many arguments. (expected 2-3, got {len(argv) - 1})")
        return
    elif len(argv) == 3:
        modifiers = []
        prog_path = argv[1]
        stdin_path = argv[2]
    elif len(argv) == 4:
        if not argv[1].startswith("-"):
            print("Invalid arguments")
            return

        modifiers = list(argv[1][1:])
        prog_path = argv[2]
        stdin_path = argv[3]

    if not prog_path.endswith(".ic"):
        print("Invalid program file extension. (expected .ic)")
        return

    if not stdin_path.endswith(".txt"):
        print("Invalid stdin file extension. (expected .txt)")
        return

    try:
        with open(prog_path) as file:
            program_data = file.read()
    except:
        print("Program file reading failed.")
        return

    try:
        with open(stdin_path) as file:
            stdin_data = file.read()
    except:
        print("Stdin file reading failed.")
        return

    try:
        program = [int(value) for value in program_data.split(",")]
    except:
        print("Malformed program.")
        return

    try:
        if "A" in modifiers:
            stdin = [ord(char) for char in stdin_data]
        elif not stdin_data:
            stdin = []
        else:
            stdin = [int(value) for value in stdin_data.split("\n")]
    except:
        print("Malformed stdin.")
        return

    vm = Intcode(program)
    for value in stdin:
        if vm.read_input(value):
            break

        if "a" in modifiers:
            print("".join(map(str, vm.read_output_all())), end="")
        else:
            for output in vm.read_output_all():
                print(output)
    else:
        EOF = 0x04 if "A" in modifiers else -1
        while not vm.read_input(EOF):
            if "a" in modifiers:
                print("".join(map(str, vm.read_output_all())), end="")
            else:
                for output in vm.read_output_all():
                    print(output)
    
    if "a" in modifiers:
        print("".join(map(str, vm.read_output_all())))
    else:
        for output in vm.read_output_all():
            print(output)


if __name__ == "__main__":
    main()

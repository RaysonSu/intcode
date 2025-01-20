from __future__ import annotations
from sys import argv
from os.path import isfile
from os import remove

import re

OPCODE_DATA: list[str] = ["add", "mul", "inp", "out", "jfp", "jfz", "ltn", "ieq", "srb", "hlt", "lit"]
OPERAND_DATA: dict[str, tuple[int, ...]] = {
    "add": (0, 0, 1),
    "mul": (0, 0, 1),
    "inp": (1, ),
    "out": (0, ),
    "jfp": (0, 0),
    "jfz": (0, 0),
    "ltn": (0, 0, 1),
    "ieq": (0, 0, 1),
    "srb": (0, ),
    "hlt": (),
    "lit": (2, )
}

def clean_lines(string: str) -> str:
    return "\n".join(line.strip() for line in string.replace(":", ":\n").split("\n") if line.strip())


def basic_validate(lines: list[str]) -> None:
    checker = re.compile(r"^((add|mul|inp|out|jfp|jfz|ltn|ieq|srb|hlt|lit)( (|.|%)(|-)(\d+|[A-Za-z_\-0-9]+))*|[A-Za-z_\-0-9]+(\+\d+|):)$")
    for row in lines:
        if not checker.match(row):
            raise ValueError(f"Invalid row: '{row}'")


def compute_index(lines: list[str]) -> list[int]:
    index = 0
    indices = []
    for row in lines:
        indices.append(index)
        first_token = row.split(" ")[0]

        match first_token:
            case "add" | "mul" | "ltn" | "ieq":
                index += 4
            case "jfp" | "jfz":
                index += 3
            case "inp" | "out" | "srb":
                index += 2
            case "hlt" | "lit":
                index += 1
            case _:
                pass
    
    return indices


def find_replacements(lines: list[str]) -> dict[str, int]:
    ret = {}
    indices = compute_index(lines)
    for row, index in zip(lines, indices):
        if any(row.startswith(operand) for operand in OPCODE_DATA):
            continue
        
        if "+" not in row:
            ret[row[:-1]] = index
        else:
            ret[row[:row.index("+")]] = index + int(row[row.index("+"):-1])
    
    return ret


def compile_asm(asm: str) -> list[int]:
    asm = clean_lines(asm)
    lines = asm.splitlines()

    basic_validate(lines)

    replacements = find_replacements(lines)
    ret = []

    is_replacement = re.compile(r"[A-Za-z_\-0-9]+(\+\d+|):")

    for row in lines:
        tokens = row.split(" ")
        if is_replacement.match(row):
            continue
        
        opcode, *operands_raw = tokens
        operand_requirements = OPERAND_DATA[opcode]

        if len(operands_raw) != len(operand_requirements):
            raise ValueError(f"Invalid operation: {row}")

        operands = []
        opcode_extra = []
        for op_raw, op_req in zip(operands_raw, operand_requirements):
            param_mode = op_raw[0]
            if param_mode == "." and op_req > 0 \
            or param_mode == "%" and op_req > 1:
                raise ValueError(f"Invalid operation param mode: {row}")
            
            match param_mode:
                case ".":
                    opcode_extra.append(1)
                    param_str = op_raw[1:]
                case "%":
                    opcode_extra.append(2)
                    param_str = op_raw[1:]
                case _:
                    opcode_extra.append(0)
                    param_str = op_raw
            
            if not (param_str.isdigit() \
            or (param_str[0] == "-" and param_str[1:].isdigit())):
                if param_str not in replacements:
                    raise ValueError(f"Invalid replacement: {param_str}")
                else:
                    operands.append(replacements[param_str])
            else:
                operands.append(int(param_str))

        extra = int("".join(map(str, opcode_extra))[::-1] + "00")
        match tokens[0]:
            case "add":
                ret.append(1 + extra)
            case "mul":
                ret.append(2 + extra)
            case "inp":
                ret.append(3 + extra)
            case "out":
                ret.append(4 + extra)
            case "jfp":
                ret.append(5 + extra)
            case "jfz":
                ret.append(6 + extra)
            case "ltn":
                ret.append(7 + extra)
            case "ieq":
                ret.append(8 + extra)
            case "srb":
                ret.append(9 + extra)
            case "hlt":
                ret.append(99)
        
        ret.extend(operands)

    return ret


def main() -> None:
    if len(argv) < 3:
        raise ValueError(f"Too few arguments. (expected 2, got {len(argv) - 1})")
    elif len(argv) > 3:
        raise ValueError(f"Too many arguments. (expected 2, got {len(argv) - 1})")
    elif len(argv) == 3:
        asm_path = argv[1]
        out_path = argv[2]

    if not asm_path.endswith(".aic"):
        raise ValueError("Invalid assembly file extension. (expected .aic)")
    
    if not out_path.endswith(".ic"):
        raise ValueError("Invalid output file extension. (expected .ic)")
    
    try:
        with open(asm_path) as file:
            asm_data = file.read()
    except:
        raise ValueError("Assembly file reading failed.")

    result = compile_asm(asm_data)

    if isfile(out_path):
        remove(out_path)

    try:
        with open(out_path, "x") as file:
            file.write(",".join(str(num) for num in result))
    except:
        raise ValueError("Outputing program failed.")

if __name__ == "__main__":
    main()
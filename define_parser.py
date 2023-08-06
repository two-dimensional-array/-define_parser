import re
import json
import sys
import getopt
from typing import IO
import subprocess

DEFINE_PATTERN = re.compile(r'^[\t ]*#[\t ]*define[\t ]+([a-zA-Z0-9_]+)(?:\s+|\Z)')
C_COMMENT_PATTERN = re.compile(r'/\*([^*]+|\*+[^/])*(\*+/)?')
CPP_COMMENT_PATTERN = re.compile(r'//.*')
VAR_PATTERN =  re.compile(r'^\t* *auto +var_([a-zA-Z0-9_]+) *= *(.+);')

def get_defines(fp: IO) -> dict:
    defines = {}
    for line in fp.readlines():
        match = DEFINE_PATTERN.match(line)
        if not match is None:
            macro_name = match.group(1)
            value = line[match.end():]
            if value == "":
                value = None
            else:
                for pattern in (C_COMMENT_PATTERN, CPP_COMMENT_PATTERN):
                    value = pattern.sub(' ', value)
                value = sub_defines_to_string(defines, value.strip())
            defines.update({macro_name : value})

    return defines

def sub_defines_to_string(defines: dict, string: str) -> str:
    for macro_name, value in defines.items():
        if not value is None:
            string = re.sub(f'(?<=[^\d\w_])({macro_name})(?=[^\d\w_])', value, string)

    return string

def main(argv: list[str]):
    header_file = ""
    json_file = ""
    include_file = ""
    define_file = ""
    substitute_file = ""
    defines_buffer = {}
    cmd = "g++ -E defines.cpp -o defines.out"

    # Processing command line arguments.
    opts, args = getopt.getopt(argv, "h:j:f:i:d:", ["header=", "json=", "flags=", "include=", "define=", "substitute="])
    for opt, arg in opts:
        if opt in ("-h", "--header"):
            header_file = arg
        elif opt in ("-j", "--json"):
            json_file = arg
        elif opt in ("-f", "--flags"):
            cmd += f" {arg}"
        elif opt in ("-i", "--include"):
            include_file = arg
        elif opt in ("-d", "--define"):
            define_file = arg
        elif opt in ("-s", "--substitute"):
            substitute_file = arg

    # Parsing the header file and extracting all macro names (#defines) into buffer.
    with open(header_file, "r") as header:
        defines_buffer = get_defines(header)
    
    # Generate source file
    with open("./defines.cpp", "w") as build:
        build.write(f"#include \"{header_file}\"\n\n")
        build.write("int main()\n")
        build.write("{\n")
        for define in defines_buffer.keys():
            if defines_buffer.get(define) != None:
                build.write(f"\tauto var_{define} = {define};\n")
        build.write("\treturn 0;\n")
        build.write("}\n")

    # Add include files path to compilation command
    if include_file != "":
        with open(include_file, "r") as include:
            for line in include.readlines():
                line = line.replace("\n", " ")
                cmd += f" -I \"{line}\""

    # Add defines to compilation command
    if define_file != "":
        with open(define_file, "r") as define:
            for line in define.readlines():
                line = line.replace("\n", " ")
                cmd += f" -D {line}"

    # Generate defines values by precompiled file
    subprocess.Popen(cmd, shell=True).wait()

    # Get defines values from precompiled file
    with open("./defines.out", "r") as pre_build:
        for line in pre_build.readlines():
            match = VAR_PATTERN.match(line)
            if not match is None:
                macro_name = match.group(1)
                value = match.group(2)
                defines_buffer.update({macro_name : value})

    # Delete temporary files
    subprocess.Popen("rm defines.cpp defines.out", shell=True)

    # Generation a json with all macro names (#defines).
    if json_file != "":
        with open(json_file, "w") as out:
            json.dump(defines_buffer, out, indent=1)

    # Modifying existing output source file to use all parsed macro names.
    if substitute_file != "":
        with open(substitute_file, "r+") as substitute:
            substitute_text = substitute.read()
            substitute.seek(0)
            substitute.truncate(0)
            substitute.write(sub_defines_to_string(defines_buffer, substitute_text))

if __name__ == '__main__':
    main(sys.argv[1:])

import re
import json
import sys
import getopt
from typing import IO

DEFINE_PATTERN = re.compile(r'^[\t ]*#[\t ]*define[\t ]+([a-zA-Z0-9_]+)(?:\s+|\Z)')
C_COMMENT_PATTERN = re.compile(r'/\*([^*]+|\*+[^/])*(\*+/)?')
CPP_COMMENT_PATTERN = re.compile(r'//.*')

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

    return string;

def main(argv: list[str]):
    header_file = ""
    defines_file = ""
    output_file = ""
    defines_buffer = {}

    # Processing command line arguments.
    opts, args = getopt.getopt(argv, "i:j:o:", ["input=", "json=", "output="])
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            header_file = arg
        elif opt in ("-j", "--json"):
            defines_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg

    # Parsing the header file and extracting all macro names (#defines) into buffer.
    with open(header_file, "r") as header:
        defines_buffer = get_defines(header)

    # Generation a json with all macro names (#defines).
    with open(defines_file, "w") as out:
        json.dump(defines_buffer, out, indent=1)
    
    # Modifying existing output source file to use all parsed macro names.
    with open(output_file, "r+") as output:
        output_text = output.read()
        output.seek(0)
        output.truncate(0)
        output.write(sub_defines_to_string(defines_buffer, output_text))

if __name__ == '__main__':
    main(sys.argv[1:])

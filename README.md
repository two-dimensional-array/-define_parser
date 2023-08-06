# Define Parser
Extract macro values (#define) from the header file and store in a readable format.
---
## Command Line Arguments
- **-h | --header**     - Path to the header file that should be parsed.
- **-j | --json**       - Path to JSON file, which contain all parsed macro names.
- **-h | --flags**      - Compilation flags.
- **-i | --include**    - Path to include path file.
- **-d | --define**     - Path to defines file.
- **-s | --substitute** - Path to file, in which need substitute defines values.
---
## Startup Define Parser script
Example of command startup [define parser][define_parser.py] script. In this repository example of command startup is located in [Makefile][startup_command] file.
```bash
~/repository_directory/python define_parser.py -h header.h -j defines.json -s main.c
```
## Example of output JSON file
In this repository example of JSON file is [defines.json][defines.json] file.
```json
{
 "macro_name1": "value",
 "macro_name2": "value",
 "macro_name3": "value"
}
```
---
[define_parser.py]: https://github.com/two-dimensional-array/define_parser/blob/master/define_parser.py
[defines.json]: https://github.com/two-dimensional-array/define_parser/blob/master/Hello_World/defines.json
[startup_command]: https://github.com/two-dimensional-array/define_parser/blob/2f6741f37c8cbd32dee30004341dc64ddf84db81/Hello_World/Makefile#L131

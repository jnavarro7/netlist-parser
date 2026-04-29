import argparse
import os
import re
import sys

def arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_file')
    ap.add_argument('--verbose', default='no', choices=['yes', 'no'])
    args = ap.parse_args()

    # Check if the input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: The file '{args.input_file}' does not exist.")
        sys.exit(1)

    # return args.input_file
    return args

def read_input_file(file_path, verbose):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Debug - print original Netlist
            if verbose:
                print(f"Original Netlist Content:\n{content}")
            return content
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def preprocess_netlist(netlist_content):
    # Pre-process file by removing comments and merging multiline statements to single line

    # Remove comments
    content = re.sub(r'//.*', '', netlist_content, flags=re.MULTILINE)

    # Merge multiline statements into single line
    lines = content.split('\n')
    merged_lines = []
    buffer = ""

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # buffer += " " + line
        buffer += line

        # Look for semicolon to determine the end of a statement
        if ';' in line:
            merged_lines.append(buffer.strip())
            buffer = ""

    # Flush any remaining buffered content (e.g., last statement at EOF without ';')
    if buffer:
        merged_lines.append(buffer.strip())

    return '\n'.join(merged_lines)

def extract_modules(content):
    # Regular expression pattern to match module sections, starts with module and ends with endmodule, capturing the module name and its body
    pattern = r'module\s+(\w+)\s*\(.*?\);\s*(.*?)endmodule'

    # Find all matches in the content
    matches = re.findall(pattern, content, re.DOTALL)

    # Initialize a dictionary to store module names and their instances
    modules = {}

    for module_name, body in matches:
        modules[module_name] = []

        lines = body.split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines and lines that do not end with a semicolon
            if not line or not line.endswith(';'):
                continue

            # skip non-instance lines input, output and wire as these do not provide value to the excersise
            if line.startswith(("input", "output", "wire")):
                continue

            # extract the instance type from the line, due to the netlist provided I can tell that instances contain ports delimted in parenthesis, so I can use that as a marker to identify instance lines.
            if '(' in line:
                tokens = line.split()
                instance_type = tokens[0]
                modules[module_name].append(instance_type)

    return modules


def count_instances(module_name, modules):
    # Initialize a dictionary to store the counts of instances
    counts = {}

    # If it is not a module it is treated as a primitive, no recursion is executed
    if module_name not in modules:
        return counts

    for instance_type in modules[module_name]:

        # count this instance
        counts[instance_type] = counts.get(instance_type, 0) + 1

        # recurse if it is a module
        if instance_type in modules:
            sub_counts = count_instances(instance_type, modules)

            for k, v in sub_counts.items():
                counts[k] = counts.get(k, 0) + v

    return counts

def main():
    # input_file = arguments()
    args = arguments()

    verbose = (args.verbose == 'yes')

    if verbose:
        print ('Verbose enabled')
    
    netlist_content = read_input_file(args.input_file, verbose)

    # Pre-process the netlist by removing comments
    preprocessed_content = preprocess_netlist(netlist_content)
       
    # Debug - print preprocessed Netlist
    if verbose:
        print(f"Preprocessed Netlist Content:\n{preprocessed_content}")

    # Extract the modules and instances
    modules = extract_modules(preprocessed_content)

    for module in modules:
        print(f"\nModule: {module}")

        result = count_instances(module, modules)

        for k, v in result.items():
            print(f"{k} : {v} placements") 

if __name__ == "__main__":
    main()
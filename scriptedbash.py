import sys
import os

def scriptedbash_to_bash(script):
    lines = script.strip().split('\n')
    bash_script = ""
    variable_map = {}

    for line in lines:
        line = line.strip()

        if line.startswith("shabang"):
            # Extract the shebang path and add it to the bash script
            path = line.split('"')[1]
            bash_script += f"#!{path}\n\n"

        elif line.startswith("define"):
            # Handle variable definition
            parts = line.split('=')
            var_name = parts[0].split()[1].strip()
            var_value = parts[1].strip()
            bash_var_name = f"var_{var_name}"  # create a bash-friendly variable name
            variable_map[var_name] = bash_var_name  # map ScriptedBash var name to Bash var name
            bash_script += f'{bash_var_name}="{var_value}"\n'

        elif line.startswith("if") or line.startswith("else if"):
            # Handle if and else-if statements
            condition_start = line.find("(")
            condition_end = line.find(")")
            condition = line[condition_start+1:condition_end]
            bash_condition = condition

            for var_name in variable_map.keys():
                # Replace ScriptedBash variables with Bash variables
                bash_condition = bash_condition.replace(var_name, variable_map[var_name])

            if line.startswith("if"):
                bash_script += f"if [ {bash_condition} ]; then\n"
            else:
                bash_script += f"elif [ {bash_condition} ]; then\n"

        elif line.startswith("println"):
            # Handle print statement
            message = line.split('"')[1]
            bash_script += f'echo "{message}"\n'

        elif line.startswith("run"):
            # Handle run command
            command = line.split('"')[1]
            bash_script += f"{command}\n"

        elif line.startswith("srun"):
            # Handle sudo run command
            command = line.split('"')[1]
            if command == "request":
                bash_script += "sudo echo \"\" # empty sudo command to make it so the user doesn't have to repeatedly type pass in\n"
            else:
                bash_script += f"sudo {command}\n"

        elif line == "end":
            bash_script += "fi\n"

        # Add more cases here as needed for other ScriptedBash structures

    return bash_script

if len(sys.argv) != 2:
    print("Usage: python3 scriptedbash.py <path_to_scriptedbash_file>")
    sys.exit(1)

file_path = sys.argv[1]

try:
    with open(file_path, 'r') as file:
        scriptedbash_code = file.read()
        bash_script = scriptedbash_to_bash(scriptedbash_code)

    # Determine the output file path
    base, _ = os.path.splitext(file_path)
    output_file_path = base + ".sh"

    with open(output_file_path, 'w') as output_file:
        output_file.write(bash_script)

    print(f"Bash script written to {output_file_path}")

except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

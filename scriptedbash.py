import sys
import os
import re

def check_syntax(script):
    lines = script.strip().split('\n')
    defined_variables = set()
    valid_commands = {"shabang", "define", "defineInt", "if", "else if", "else", "println", "run", "srun", "end", "while", "bash", "wend", "increase", "for", "fend"}
    if_stack = []  # Stack to keep track of if/else if statements

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith("##"):
            continue

        # Extract the command (word before first space or opening parenthesis)
        command = re.match(r"^[a-zA-Z]+\b", line)
        if command:
            command = command.group()
        else:
            return False, f"Invalid syntax on line {line_number}"

        if command not in valid_commands:
            return False, f"Invalid command on line {line_number}: {command}"

        if command == "define":
            var_name = line.split()[1]
            defined_variables.add(var_name)

        if command in {"if", "else if"}:
            # Check for balanced parentheses in conditions
            condition = line[line.find("(")+1:line.find(")")]
            if condition.count("(") != condition.count(")"):
                return False, f"Unbalanced parentheses in condition on line {line_number}"

            # Check if variables in condition are defined
            tokens = condition.split()
            for token in tokens:
                if token in defined_variables or not token.isalpha():
                    continue
                return False, f"Undefined variable used in condition on line {line_number}: {token}"

            if_stack.append(line_number)  # Push the line number of the if/else if statement

        if command == "end":
            if not if_stack:
                return False, f"Unmatched 'end' found on line {line_number}"
            if_stack.pop()  # Pop the matching if/else if statement

    if if_stack:
        return False, f"Missing 'end' for if/else if started on line {if_stack[-1]}"

    return True, "Syntax check passed"

def scriptedbash_to_bash(script):
    lines = script.strip().split('\n')
    bash_script = ""
    variable_map = {}

    #print(lines)

    for line in lines:
        line = line.strip()
        #print(line)
        if line.startswith("shabang"):
            # Extract the shebang path and add it to the bash script
            path = line.split('"')[1]
            bash_script += f"#!{path}\n\n"

        elif line.startswith("##"):
            # Ignore comments
            continue

        elif line.startswith("define "):
            parts = line.split('=', 1)  # Split on the first '=' only
            #print(parts)
            var_name = parts[0].split()[1].strip()
            var_value = parts[1].strip()

            if "userinput" in var_value:
                prompt_index = var_value.find('"')
                if prompt_index != -1:
                    # Extract the prompt
                    prompt = var_value[prompt_index+1:var_value.rfind('"')]
                    bash_script += f'echo -n "{prompt} "; read {var_name}\n'
                else:
                    # No prompt, just use read
                    bash_script += f'echo -n "Enter value for {var_name}: "; read {var_name}\n'
            elif "math" in var_value:
                # Handle mathematical operation
                condition_start = var_value.find("(")
                condition_end = var_value.find(")")
                math_expression = var_value[condition_start + 1:condition_end]

                # Replace ScriptedBash variables with Bash variables in the math expression
                for var_in_expression in variable_map:
                    math_expression = math_expression.replace(var_in_expression, f"${variable_map[var_in_expression]}")

                bash_script += f'let "{var_name}={math_expression}"\n'

            else:
                # Handle normal variable definition
                var_value = var_value.strip('"')
                bash_script += f'{var_name}="{var_value}"\n'
            
            # Add variable to the map
            variable_map[var_name] = var_name

        elif line.startswith("defineInt "):
            parts = line.split('=', 1)  # Split on the first '=' only
            var_name = parts[0].split()[1].strip()
            var_value = parts[1].strip()

            if "math" in var_value:
                # Handle mathematical operation for integer
                condition_start = var_value.find("(")
                condition_end = var_value.find(")")
                math_expression = var_value[condition_start + 1:condition_end]

                # Replace ScriptedBash variables with Bash variables in the math expression
                for var_in_expression in variable_map:
                    math_expression = math_expression.replace(var_in_expression, f"${variable_map[var_in_expression]}")

                bash_script += f'let "{var_name}={math_expression}"\n'
            else:
                # Handle normal integer variable definition
                bash_script += f'{var_name}={var_value}\n'

            # Add variable to the map
            variable_map[var_name] = var_name

        elif line.startswith("if") or line.startswith("else if") or line.startswith("else"):
            # Handle if and else-if statements
            condition_start = line.find("(")
            condition_end = line.find(")")
            condition = line[condition_start + 1:condition_end]

            # Prepare the Bash condition string
            bash_condition = ""

            # Split the condition into tokens and process each one
            tokens = condition.split()
            for token in tokens:
                if token in variable_map:
                    # Append $ to variables
                    bash_condition += f" ${variable_map[token]}"
                else:
                    # Append other elements as is
                    bash_condition += f" {token}"

            # Construct the if or elif statement
            if line.startswith("if"):
                bash_script += f"if [{bash_condition} ]; then\n"
            elif line.startswith("else if"):
                bash_script += f"elif [{bash_condition} ]; then\n"
            elif line.startswith("else"):
                bash_script += f"else\n"

        elif line.startswith("while"):
            condition_start = line.find("(")
            condition_end = line.find(")")
            condition = line[condition_start + 1:condition_end]
            bash_condition = ""
            tokens = condition.split()
            for token in tokens:
                if token in variable_map:
                    bash_condition += f" ${variable_map[token]}"
                else:
                    # Append other elements as is
                    bash_condition += f" {token}"
            bash_script += f"while [ {bash_condition} ]; do\n"

        elif line.startswith("println"):
            # Handle print statement with variable support
            message = line.split('"')[1]
            # Find and replace all [variable] occurrences with Bash variables
            variables_in_message = re.findall(r'\[([^\]]+)\]', message)
            for var in variables_in_message:
                bash_var_name = variable_map.get(var, var)  # Get the mapped bash variable name
                message = message.replace(f'[{var}]', f'${bash_var_name}')
            bash_script += f'echo "{message}"\n'

        elif line.startswith("run"):
            # Handle run command
            command = line.split('"')[1]
            bash_script += f"{command}\n"

        elif line.startswith("srun"):
            # Handle sudo run command
            command = line.split('"')[1]
            if command == "request":
                bash_script += f"sudo echo \"\"\n"
            else:
                bash_script += f"sudo {command}\n"

        elif line.startswith("increase"):
            parts = line.split(' ', 2)
            bash_script += f"(({parts[1]} += {parts[2]}))\n"

        elif line == "end":
            bash_script += "fi\n"

        elif line == "wend" or line == "fend":
            bash_script += "done\n"

        elif line.startswith("bash"):
            condition_start = line.find("(")
            condition_end = line.find(")")
            condition = line[condition_start + 1:condition_end]
            bash_script += condition + "\n"

        elif line.startswith("for"):
            condition_start = line.find("(")
            condition_end = line.find(")")
            condition = line[condition_start + 1:condition_end]
            bash_script += f"for {condition}; do\n"
        
        # Add more cases here as needed for other ScriptedBash structures

    return bash_script

if len(sys.argv) != 2:
    print("Usage: python3 scriptedbash.py <path_to_scriptedbash_file>")
    sys.exit(1)

file_path = sys.argv[1]

try:
    with open(file_path, 'r') as file:
        scriptedbash_code = file.read()
        syntax_ok, message = check_syntax(scriptedbash_code)
        if syntax_ok:
            bash_script = scriptedbash_to_bash(scriptedbash_code)
            # Determine the output file path
            base, _ = os.path.splitext(file_path)
            output_file_path = base + ".sh"

            with open(output_file_path, 'w') as output_file:
                output_file.write(bash_script)

            print(f"Bash script written to {output_file_path}")
        else:
            print(f"Syntax Error: {message}")
        #bash_script = scriptedbash_to_bash(scriptedbash_code)

except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

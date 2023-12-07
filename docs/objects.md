# Objects

## run Statement

### Syntax

```
run(<bash command>)
```

### Use

Runs bash command

### Examples

```
run("mkdir ./folder")
run("chmod +x script.sh")
```

## srun Statement

### Syntax

```
srun(<bash command>)
```

### Use

Runs bash command using sudo (assumes your system uses sudo and not doas or anything else)

### Examples

```
srun("systemctl status sshd")
```

## if Statement

### Syntax

```
if (<condition>):

end
```

### Use

Runs code is the condition is true

### Examples

```
if (arg[0] == "-a"):

    echo "-a passed to script"

end
```

## else if Statement

### Syntax

```
if (<condition>):

else if (<condition>):

end
```

### Use

Runs different set of code is the condition in a if statement is false and the condition in the else if statement is true.

### Examples

```
if (arg[0] == "-a"):

    echo "-a passed to script"

else if (arg[0] == "-b"):

    echo "-b passed to script"

end
```

## else Statement

### Syntax

```
if (<condition>):

else:

end
```

### Use

Runs different set of code is the condition in a if statement is false.

### Examples

```
if (arg[0] == "-a"):

    echo "-a passed to script"

else:

    echo "other passed to script"

end
```

## println Statement

### Syntax

```
println(<text to print>)
```

### Use

Output text to the console.

### Examples

```
println("this is a output")
```

## define Statement

### Syntax

```
define <varname> = <value>
```

### Use

Define variables to be used in other objects

### Examples

```
define variable1 = "hello"
```

## math Statement

### Syntax

```
define <varname> = math(<equation>)
## or
defineInt <varname> = math(<equation>)
```

### Use

Output a the result of a equation to a variable. Can only be used in the define object

### Examples

```
define math1 = math(10+10)
defineInt math2 = math(10+10)
```

## userinput Statement

### Syntax

```
## with prompt
define <varname> = userinput(<prompt>)
## without prompt
define <varname> = userinput()
```

### Use

Gets input from the user then outputs it into a variable. Can only be used with the define statement.

### Examples

```
## with prompt
define var1 = userinput("this is a prompt ")
## without prompt
define var2 = userinput()
```

## while Statement

### Syntax

```
while (<condition>):
## code
wend
```

### Use

Runs a command while the condition is true.

### Examples

```
while (i -le 5):
    println ("hello")
    increase i 1
wend
```

## bash Statement

### Syntax

```
bash(<line to put in file>)
```

### Use

Allows you to define a line of bash to be put into the script. This is used for when something hasnt been implemented into scriptedbash yet.

### Examples

```
bash (echo "hello")
```

## defineInt Statement

### Syntax

```
defineInt <variable name> = <value>
```

### Use

Defines a integer.

### Examples

```
defineInt i = 0
defineInt math1 = math(10+10)
```

## increase

### Syntax

```
increase <variable> <amount>
```

### Use

Increases a variable by a amount

### Examples

```
increase i 1
```
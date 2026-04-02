# Software Design Report



**Project:** VFS Shell (Virtual File System Simulator)  


**Year:** 2026

---

## 1. Updates and Changes to the Architecture (Change Log)

During the implementation of the MVP (Minimum Viable Product), several key changes were made to the initial architecture to improve flexibility and adhere to the principle of Separation of Concerns.

| Component | Was | Became | Reason for change |
|---|---|---|---|
| VFSContext | used_size attribute | get_used_space() method | Dynamic calculation of tree weight is more reliable than a static counter. |
| VFSContext | --- | is_initialized(), has_enough_space() | Encapsulation of system state checks within the context. |
| Exec Engine | Accepted ICommand | Accepts raw_line: str | The engine has become a true orchestrator: it initiates string parsing itself. |
| Exec Engine | SecurityEngine attribute | Moved to validation logic | Simplified interaction: permission checks occur immediately before command execution. |
| Formatter | apply_colors method | Integrated into render | Reduced number of small methods; color formatting is part of rendering. |

## 2. Component Diagram and Data Flow

The system is designed using the principle of loose coupling. ```main.py``` (Controller) plays a key role as an intermediary, coordinating the work of the parser and the engine.

### Data flow direction:
```User/Script``` -> ```Main (Controller) ``` -> ```Input Parser``` -> ```Command Object (returned to Main)``` -> ```Execution Engine``` -> ```Security Check``` -> ```Command.execute(Context)``` -> ```Output Formatter```.

## 3. Description of Key Classes

### 3.1. VFSContext (System State)

This class is the “single source of truth” for the entire program.
- Methods:
    - ```get_used_space()```: Recursively calculates the current amount of used memory.
    - ```has_enough_space(size)```: Checks whether new data can be written.
    - ```is_initialized()```: Ensures that operations are not performed without the mkfs command having been executed.

### 3.2. Execution Engine (Orchestrator)
Responsible exclusively for the “lifecycle” of command execution.

- Method execute(command, raw_line): Receives a ready-made object. Its responsibilities are limited to:
    1. Asking the SecurityEngine whether the action is permitted.
    2. Invoking the command execution.
    3. Passing the result to the OutputFormatter.

### 3.3. Input Parser (Text Parser)
A pure translator of text commands into program objects.

- How it works: Uses a Dispatch Table (dictionary of factories) to create commands. This eliminates the need for cumbersome ```if-elif``` constructs and allows for easy addition of new commands or aliases ```(cls/clear)```.

### 3.4. Output Formatter (Presentation Module)
The only place in the system where the use of `print` and ANSI color codes is permitted.

- Takes a ```CommandResult``` and converts it into a human-readable format (tables for ```ls```, text for ```cat```, colored statuses ```[OK]``` or ```[ERROR]```).

## 4. Justification of Data Structures

1. N-ary Tree (Composite Pattern): Allows the system to treat files and directories identically via the INode interface. This perfectly matches the hierarchical nature of file systems.

2. Hash Tables (Python Dicts):
- In Directory: For instant access to files by name (O(1)).
- In Parser: For fast mapping of strings to command classes.

3. Bitmasks: Used to store access permissions (e.g., 755). This allows security checks to be performed using fast bitwise AND operations, which mimic the actual access rights logic in Unix.

4. Command Pattern: Every action is an object. This makes it easy to implement logging, undo actions, or batch execute commands from scripts without modifying the system kernel.
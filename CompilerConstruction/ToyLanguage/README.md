# ToyLanguage Compiler Construction Project

This project implements a small toy language interpreter for Compiler Construction practice.

## Language Goal

The toy language supports:
- `dikhao("...")` as the print statement
- `btao()` as the input function
- `agar` / `yahtu` / `warna` for conditional branching
- `jabtak` for while loops
- `chalo` for for loops
- `kro jabtak` for do-while loops
- Boolean operators: `aur`, `ya`, `nahi`
- Boolean values: `sahi`, `galat`
- Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Basic arithmetic expressions
- Variables and assignment
- Comments starting with `#`

## Usage

Run a script file:

```bash
python3 toy_language.py example.toy
```

## Example

```toy
# Read a name from the user
name = btao("Enter your name: ")

dikhao("Hello", name)

agar name == "Alice" {
    dikhao("Welcome back, Alice!")
} yahtu name == "Bob" {
    dikhao("Hi Bob, nice to see you")
} warna {
    dikhao("Hello stranger")
}

# Boolean expressions
valid = sahi
allowed = galat
agar valid aur nahi allowed {
    dikhao("You can enter")
} warna {
    dikhao("Access denied")
}

agar valid ya allowed {
    dikhao("At least one condition is true")
}

# for loop with chalo
chalo i = 0; i < 3; i = i + 1 {
    dikhao("chalo loop i", i)
}

# do-while loop with kro jabtak
count = 0
kro {
    dikhao("kro jabtak loop count", count)
    count = count + 1
}
jabtak count < 2
```

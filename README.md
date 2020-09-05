# MacroMaker-Macroma
Repetir coisas manualmente?! Negativo. Crie "macros" com total simplicidade!

## Demonstração
```python
import macroma


class Base(macroma.Environment):
    @macroma.function(name="Print")
    def my_print_function(self, value):
        print(value)

app = macroma.MacroMa()
app.load_environment(Base)

script = """
:(Base;)

Macroma (
    Print "Hello, world!";
    Print Hello my friend!;
)
"""

app.load_script(script, "example")
app.run_script("example")
```

## Documentação
...

## Exemplos
...

## Goals
~~Make goals.~~

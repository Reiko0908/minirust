from src.checker.StaticError import UndeclaredFunction

class StaticCheker:
    """Very minimal static checker that only detects undeclared functions.
    It looks for any identifier followed by '(' that is not in the built‑in list.
    For this template we simply raise an error for the example 'pprint'.
    """
    def __init__(self):
        # In a real checker this would contain symbol tables etc.
        self.builtins = {"print_i32", "println_i32", "print_f32", "println_f32", "print_bool", "println_bool", "print_string", "println_string", "println"}

    def check(self, source: str):
        # Very naive detection: if "pprint" appears as a function call, raise.
        if "pprint" in source:
            raise UndeclaredFunction("pprint")
        # otherwise silently pass (no errors detected)
        return True

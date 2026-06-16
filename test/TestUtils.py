import sys
import os
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

# Add src to python path to import generated grammar and utils
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

class TestErrorListener(ErrorListener):
    def __init__(self):
        super(TestErrorListener, self).__init__()
        self.error_message = None
        self.error_line = None

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if not self.error_message:
            symbol_text = offendingSymbol.text if offendingSymbol else ""
            self.error_message = f"Error on line {line} col {column}: {symbol_text}"
            self.error_line = line

class TestLexer:
    @staticmethod
    def checkLexer(input_str, expected_output):
        from grammar.MiniRustLexer import MiniRustLexer
        from utils.lexerror import ErrorToken, UncloseString, IllegalEscape

        input_stream = InputStream(input_str)
        lexer = MiniRustLexer(input_stream)
        lexer.removeErrorListeners()

        tokens = []
        try:
            while True:
                token = lexer.nextToken()
                if token.type == Token.EOF:
                    break
                lexeme = token.text
                tokens.append(lexeme)
        except (ErrorToken, UncloseString, IllegalEscape) as err:
            tokens.append(err.message)
            
        actual_result = ", ".join(tokens)
        assert actual_result == expected_output, f"expected '{expected_output}' but got '{actual_result}'"

class TestParser:
    @staticmethod
    def checkParser(input_str, expected_error_line):
        from grammar.MiniRustLexer import MiniRustLexer
        from grammar.MiniRustParser import MiniRustParser
        from utils.lexerror import ErrorToken, UncloseString, IllegalEscape

        input_stream = InputStream(input_str)
        lexer = MiniRustLexer(input_stream)
        lexer.removeErrorListeners()

        token_stream = CommonTokenStream(lexer)
        parser = MiniRustParser(token_stream)
        parser.removeErrorListeners()

        error_listener = TestErrorListener()
        parser.addErrorListener(error_listener)

        error_line = None
        error_msg = None

        try:
            parser.program()
            if error_listener.error_message:
                error_line = error_listener.error_line
                error_msg = error_listener.error_message
        except (ErrorToken, UncloseString, IllegalEscape) as e:
            error_line = e.line
            error_msg = e.message
            
        if error_msg is not None or error_listener.error_line is not None:
            actual_error_line = error_line if error_line is not None else error_listener.error_line
            actual_result = str(actual_error_line)
        else:
            actual_result = "Success"
            
        assert actual_result != "Success", f"expected parsing to fail, but it succeeded"
        
        expected_str = str(expected_error_line)
        assert actual_result == expected_str, (
            f"expected error on line {expected_error_line} "
            f"but got error on line {actual_result} ({error_msg or error_listener.error_message})"
        )

class TestAST:
    @staticmethod
    def checkAST(input_str, expected_str):
        from grammar.MiniRustLexer import MiniRustLexer
        from grammar.MiniRustParser import MiniRustParser
        from astgen.ASTGenerator import ASTGenerator

        input_stream = InputStream(input_str)
        lexer = MiniRustLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = MiniRustParser(stream)
        tree = parser.program()
        visitor = ASTGenerator()
        ast = visitor.visit(tree)
        
        actual_result = str(ast)
        
        res = "".join(actual_result.split())
        exp = "".join(expected_str.split())
        assert res == exp, f"Expected:\n{expected_str}\nGot:\n{actual_result}"

class TestChecker:
    @staticmethod
    def checkChecker(ast_obj, expected_output):
        if isinstance(ast_obj, str):
            from grammar.MiniRustLexer import MiniRustLexer
            from grammar.MiniRustParser import MiniRustParser
            from astgen.ASTGenerator import ASTGenerator
            input_stream = InputStream(ast_obj)
            lexer = MiniRustLexer(input_stream)
            stream = CommonTokenStream(lexer)
            parser = MiniRustParser(stream)
            tree = parser.program()
            visitor = ASTGenerator()
            ast_obj = visitor.visit(tree)

        from checker.StaticChecker import StaticChecker
        from checker.StaticError import StaticError

        try:
            StaticChecker(ast_obj).check()
            actual_result = "Success"
        except StaticError as err:
            actual_result = str(err)
            
        assert actual_result == expected_output, f"expected '{expected_output}' but got '{actual_result}'"



class CodeGenerator:
    def generate_and_run(self, ast):
        if isinstance(ast, str):
            from antlr4 import InputStream, CommonTokenStream
            from grammar.MiniRustLexer import MiniRustLexer
            from grammar.MiniRustParser import MiniRustParser
            from astgen.ASTGenerator import ASTGenerator
            input_stream = InputStream(ast)
            lexer = MiniRustLexer(input_stream)
            stream = CommonTokenStream(lexer)
            parser = MiniRustParser(stream)
            tree = parser.program()
            visitor = ASTGenerator()
            ast = visitor.visit(tree)

        import subprocess
        # Get paths relative to solution directory
        base_dir = os.path.dirname(os.path.abspath(__file__)) # solution/test
        solution_dir = os.path.dirname(base_dir) # solution
        runtime_dir = os.path.join(solution_dir, "src", "runtime")

        
        # 1. Compile io.java if io.class doesn't exist
        io_java = os.path.join(runtime_dir, "io.java")
        io_class = os.path.join(runtime_dir, "io.class")
        if not os.path.exists(io_class):
            try:
                subprocess.run(["javac", "-d", runtime_dir, io_java], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to compile io.java:\n{e.stderr.decode('utf-8')}")
                
        # 2. Run student's CodeGenerator visitor to generate Jasmin files in solution/src/runtime
        from codegen.CodeGen import CodeGenerator as StudentCodeGenerator
        student_codegen = StudentCodeGenerator()
        student_codegen.visit(ast, None)
        
        # 3. Assemble generated Jasmin files to class files using jasmin.jar
        j_files = [f for f in os.listdir(runtime_dir) if f.endswith(".j")]
        if not j_files:
            raise RuntimeError("No Jasmin (.j) files generated by CodeGenerator")
            
        jasmin_jar = os.path.join(runtime_dir, "jasmin.jar")
        for j_file in j_files:
            j_path = os.path.join(runtime_dir, j_file)
            try:
                subprocess.run(["java", "-jar", jasmin_jar, "-d", runtime_dir, j_path], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                # Read the Jasmin file contents for debugging info
                with open(j_path, "r") as f:
                    j_content = f.read()
                raise RuntimeError(f"Jasmin assembly failed for {j_file}:\n{e.stderr.decode('utf-8')}\nJasmin File Content:\n{j_content}")
                
        # 4. Execute the MiniRustProgram class and capture stdout
        try:
            result = subprocess.run(
                ["java", "-cp", runtime_dir, "MiniRustProgram"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            stdout = result.stdout
        except subprocess.TimeoutExpired:
            # Clean up generated .j and .class files (except jasmin.jar and io.class)
            for f in os.listdir(runtime_dir):
                if f in ["jasmin.jar", "io.class", "io.java"]:
                    continue
                if f.endswith(".j") or f.endswith(".class"):
                    try:
                        os.remove(os.path.join(runtime_dir, f))
                    except OSError:
                        pass
            raise RuntimeError("Execution timed out (potential infinite loop)")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Execution failed:\n{e.stderr}\n{e.stdout}")
            
        # 5. Clean up generated .j and .class files (except jasmin.jar and io.class)
        for f in os.listdir(runtime_dir):
            if f in ["jasmin.jar", "io.class", "io.java"]:
                continue
            if f.endswith(".j") or f.endswith(".class"):
                try:
                    os.remove(os.path.join(runtime_dir, f))
                except OSError:
                    pass
                    
        return stdout


import sys
import subprocess
import os

def print_usage():
    print("Usage:")
    print("  python run.py gen                 - Generate Lexer and Parser using ANTLR4")
    print("  python run.py test-lexer [file]   - Run Lexer tests (default: test/test-lexer.py)")
    print("  python run.py test-parser [file]  - Run Parser tests (default: test/test-parser.py)")
    print("  python run.py test-ast [file]     - Run AST tests (default: test/test-ast.py)")
    print("  python run.py test-checker [file] - Run Checker tests (default: test/test-checker.py)")
    print("  python run.py test-codegen [file] - Run Codegen tests (default: test/test-codegen.py)")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # Determine the directory paths relative to the solution directory
    src_dir = os.path.dirname(os.path.abspath(__file__))
    solution_dir = os.path.dirname(src_dir)
    grammar_dir = os.path.join(src_dir, 'grammar')
    g4_path = os.path.join(grammar_dir, 'MiniRust.g4')

    command = sys.argv[1]

    if command == "gen":
        print(f"Generating Lexer and Parser from {g4_path}...")
        # Check if grammar file exists
        if not os.path.exists(g4_path):
            print(f"Error: Grammar file not found at {g4_path}")
            sys.exit(1)
        
        # Build command: try antlr4 first, then antlr if not found
        success = False
        errors = []
        for cmd_name in ["antlr4", "antlr"]:
            cmd = [cmd_name, "-Dlanguage=Python3", "-visitor", "-o", grammar_dir, g4_path]
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                print(f"Successfully generated Lexer and Parser using {cmd_name}.")
                if result.stdout:
                    print(result.stdout)
                success = True
                break
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while running {cmd_name}:")
                print(e.stderr)
                sys.exit(1)
            except FileNotFoundError:
                errors.append(f"'{cmd_name}' not found")
        
        if not success:
            print("Error: Neither 'antlr4' nor 'antlr' command was found in PATH.")
            print("Please install ANTLR4 and ensure it is in your PATH.")
            sys.exit(1)

    elif command in ["test-lexer", "test-parser", "test-ast", "test-checker", "test-codegen"]:
        print(f"Running {command} tests...")
        
        default_files = {
            "test-lexer": "test-lexer.py",
            "test-parser": "test-parser.py",
            "test-ast": "test-ast.py",
            "test-checker": "test-checker.py",
            "test-codegen": "test-codegen.py"
        }
        
        if len(sys.argv) >= 3:
            test_path = sys.argv[2]
        else:
            test_path = os.path.join(solution_dir, 'test', default_files[command])
            
        extra_args = sys.argv[3:]
        
        # Hide tracebacks and suppress individual test output for private tests
        if os.path.basename(test_path) == "test-private.py":
            if not any(arg.startswith("--tb=") for arg in extra_args):
                extra_args.append("--tb=no")
            if "-q" not in extra_args and "--quiet" not in extra_args:
                extra_args.append("-q")
        
        env = os.environ.copy()
        test_dir = os.path.join(solution_dir, 'test')
        src_dir = os.path.join(solution_dir, 'src')
        
        # Add src and its sub-directories to PYTHONPATH so that we don't need conftest.py
        sub_paths = [
            src_dir,
            os.path.join(src_dir, 'grammar'),
            os.path.join(src_dir, 'astgen'),
            os.path.join(src_dir, 'checker'),
            os.path.join(src_dir, 'codegen'),
            os.path.join(src_dir, 'utils')
        ]
        
        new_pythonpath = os.pathsep.join([test_dir] + sub_paths)
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = new_pythonpath + os.pathsep + env['PYTHONPATH']
        else:
            env['PYTHONPATH'] = new_pythonpath

        cmd = [sys.executable, "-m", "pytest", "-v", test_path] + extra_args
        
        # Run pytest
        subprocess.run(cmd, env=env)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()

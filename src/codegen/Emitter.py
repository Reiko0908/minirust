"""
Emitter class for MiniRust code generation.
High-level code emission with type conversion, constant loading, variable operations.
"""

import os

from codegen.Error import IllegalOperandException
from codegen.JasminCode import JasminCode
from codegen.Utils import FunctionType
from codegen.Utils import StructType as CodeGenStructType
from utils.AST import (
    ArrayType,
    BoolType,
    FloatType,
    Id,
    IntType,
    StringType,
    StructType,
    VoidType,
)


# -----------------------------------------------
# MiniRust type helpers
# ------------------------------------------------
def is_int_type(in_type):
    """Check if type is int."""
    return isinstance(in_type, IntType)

def is_float_type(in_type):
    """Check if type is float."""
    return isinstance(in_type, FloatType)

def is_bool_type(in_type):
    """Check if type is bool."""
    return isinstance(in_type, BoolType)

def is_string_type(in_type):
    """Check if type is string."""
    return isinstance(in_type, StringType)

def is_void_type(in_type):
    """Check if type is void."""
    return isinstance(in_type, VoidType)

def is_array_type(in_type):
    """Check if type is array."""
    return isinstance(in_type, ArrayType)

def is_struct_type(in_type):
    """Check if type is struct."""
    return isinstance(in_type, (StructType, CodeGenStructType))

def is_reference_type(in_type):
    """Check if a value uses JVM reference instructions"""
    return (
        is_string_type(in_type)
        or is_struct_type(in_type)
        or is_array_type(in_type)
    )

class Emitter:
    """
    Emitter class to generate JVM bytecode instructions for MiniRust.

    Attributes:
        filename (str): Name of the output file
        buff (List[str]): Buffer to store generated code
        jvm (JasminCode): JasminCode instance for JVM instruction generation
    """

    def __init__(self, filename: str):
        """
        Initialize Emitter.

        Args:
            filename: Name of the output file (.j file)
        """
        self.filename = filename
        self.filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "runtime", filename
        )
        self.buff: list[str] = []
        self.jvm = JasminCode()

    def get_jvm_type(self, in_type) -> str:
        """
        Convert MiniRust AST type to JVM type descriptor.

        Args:
            in_type: AST type to convert

        Returns:
            JVM type descriptor string
        """
        if is_int_type(in_type):
            return "I"
        elif is_float_type(in_type):
            return "F"
        elif is_bool_type(in_type):
            return "Z"
        elif is_string_type(in_type):
            return "Ljava/lang/String;"
        elif is_void_type(in_type):
            return "V"
        elif is_array_type(in_type):
            return "[" + self.get_jvm_type(in_type.element_type)
        elif is_struct_type(in_type):
            struct_name = in_type.name if hasattr(in_type, 'name') else in_type.struct_name
            if isinstance(struct_name, Id):
                struct_name = struct_name.name
            return "L" + str(struct_name) + ";"
        elif isinstance(in_type, FunctionType):
            params = "".join(map(self.get_jvm_type, in_type.param_types))
            return f"({params}){self.get_jvm_type(in_type.return_type)}"
        else:
            raise IllegalOperandException(f"Unknown type: {type(in_type)}")

    # -------------------------------------------
    # Constants and local variables
    # -------------------------------------------
    def emit_push_iconst(self, in_: int | str, frame) -> str:
        """
        Emit instruction to push integer constant onto operand stack.

        Args:
            in_: Integer value or string representation
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        if in_ == "true":
            value = 1
        elif in_ == "false":
            value = 0
        else:
            value = int(in_)
        frame.push()

        if -1 <= value <= 5:
            return self.jvm.emitICONST(value)
        elif -128 <= value <= 127:
            return self.jvm.emitBIPUSH(value)
        elif -32768 <= value <= 32767:
            return self.jvm.emitSIPUSH(value)
        return self.jvm.emitLDC(str(value))

    def emit_push_fconst(self, in_: str, frame) -> str:
        """
        Emit instruction to push float constant onto operand stack.

        Args:
            in_: String representation of float value
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        value = float(in_)
        text = repr(value)
        frame.push()
        if value == 0.0 and text.startswith('-'):
            return self.jvm.emitLDC("-0.0")
        if value in (0.0, 1.0, 2.0):
            return self.jvm.emitFCONST(f"{value:.1f}")
        return self.jvm.emitLDC(text)

    def emit_push_const(self, in_: str, typ, frame) -> str:
        """
        Generate code to push a constant onto the operand stack.

        Args:
            in_: The lexeme of the constant
            typ: The type of the constant
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string

        Raises:
            IllegalOperandException: If type is not supported
        """
        if is_int_type(typ) or is_bool_type(typ):
            return self.emit_push_iconst(in_, frame)
        elif is_float_type(typ):
            return self.emit_push_fconst(in_, frame)
        elif is_string_type(typ):
            frame.push()
            # String literals - in_ already contains the string value (without quotes)
            # For JVM LDC, we need to properly escape the string
            # Escape backslashes and quotes
            escaped = in_.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            return self.jvm.emitLDC(f'"{escaped}"')
        else:
            raise IllegalOperandException(f"Unsupported constant type: {type(typ)}")

    def emit_push_null(self, frame) -> str:
        """Push a JVM null reference."""
        frame.push()
        return self.jvm.emitPUSHNULL()

    def emit_var(self, in_: int, var_name: str, in_type, from_label: int, to_label: int, desc: str | None = None) -> str:
        """
        Generate the var directive for a local variable.

        Args:
            in_: The index of the local variable
            var_name: The name of the local variable
            in_type: The type of the local variable
            from_label: The starting label of the scope where the variable is active
            to_label: The ending label of the scope where the variable is active

        Returns:
            Generated var directive string
        """
        return self.jvm.emitVAR(
            in_, var_name, desc or self.get_jvm_type(in_type), from_label, to_label
        )

    def emit_read_var(self, name: str, in_type, index: int, frame) -> str:
        """
        Emit instruction to read local variable.

        Args:
            name: Variable name
            in_type: Variable type
            index: Variable index
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string

        Raises:
            IllegalOperandException: If type is not supported
        """
        frame.push()
        if is_int_type(in_type) or is_bool_type(in_type):
            return self.jvm.emitILOAD(index)
        elif is_float_type(in_type):
            return self.jvm.emitFLOAD(index)
        elif is_reference_type(in_type):
            return self.jvm.emitALOAD(index)
        else:
            raise IllegalOperandException(f"Unsupported variable type: {type(in_type)}")

    def emit_write_var(self, name: str, in_type, index: int, frame) -> str:
        """
        Generate code to pop a value on top of the operand stack and store it to a block-scoped variable.

        Args:
            name: The symbol entry of the variable
            in_type: Variable type
            index: Variable index
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string

        Raises:
            IllegalOperandException: If type is not supported
        """
        frame.pop()
        if is_int_type(in_type) or is_bool_type(in_type):
            return self.jvm.emitISTORE(index)
        elif is_float_type(in_type):
            return self.jvm.emitFSTORE(index)
        elif is_reference_type(in_type):
            return self.jvm.emitASTORE(index)
        else:
            raise IllegalOperandException(f"Unsupported variable type: {type(in_type)}")

    # -------------------------------------------
    # Fields and invocations
    # -------------------------------------------
    def emit_get_static(self, lexeme: str, in_, frame, desc: str | None = None) -> str:
        """Read a static field and track the pushed value."""
        frame.push()
        return self.jvm.emitGETSTATIC(lexeme, desc or self.get_jvm_type(in_))

    def emit_put_static(self, lexeme: str, in_, frame, desc: str | None = None) -> str:
        """Write to a static field and track the consumed value."""
        frame.pop()
        return self.jvm.emitPUTSTATIC(lexeme, desc or self.get_jvm_type(in_))

    def emit_get_field(self, lexeme: str, in_, frame, desc: str | None = None) -> str:
        """
        Emit GETFIELD instruction for struct member access.

        Args:
            lexeme: Field name (struct_name/member_name)
            in_: Field type
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        # GETFIELD pops object reference, pushes field value
        frame.pop()  # Pop object reference
        frame.push()  # Push field value
        return self.jvm.emitGETFIELD(lexeme, desc or self.get_jvm_type(in_))

    def emit_put_field(self, lexeme: str, in_, frame, desc: str | None = None) -> str:
        """
        Emit PUTFIELD instruction for struct member assignment.

        Args:
            lexeme: Field name (struct_name/member_name)
            in_: Field type
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        frame.pop()
        return self.jvm.emitPUTFIELD(lexeme, desc or self.get_jvm_type(in_))

    def emit_invoke_static(self, lexeme: str, in_, frame, desc: str | None = None) -> str:
        """
        Generate code to invoke a static method.

        Args:
            lexeme: The qualified name of the method (class-name/method-name)
            in_: The type descriptor of the method
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        typ = in_
        list(map(lambda x: frame.pop(), typ.param_types))
        if not is_void_type(typ.return_type):
            frame.push()
        return self.jvm.emitINVOKESTATIC(lexeme, desc or self.get_jvm_type(in_))

    def emit_invoke_special(self, lexeme: str, in_, frame, desc: str | None = None) -> str:
        """Invoke an instance initializer or private instance method."""
        list(map(lambda x: frame.pop(), in_.param_types))
        frame.pop()
        if not is_void_type(in_.return_type):
            frame.push()
        code = self.jvm.emitINVOKESPECIAL(lexeme, desc or self.get_jvm_type(in_))
        assert code is not None
        return code

    # -------------------------------------------
    # MiniRust array operations
    # -------------------------------------------
    def emit_array_load(self, element_type, frame) -> str:
        """Load one array element, replacing array/idx with its value."""
        frame.pop()
        if is_bool_type(element_type):
            return "\tbaload\n"
        elif is_int_type(element_type):
            return self.jvm.emitIALOAD()
        elif is_float_type(element_type):
            return self.jvm.emitFALOAD()
        elif is_reference_type(element_type):
            return self.jvm.emitAALOAD()
        raise IllegalOperandException(f"Unsupported array element type: {type(element_type)}")

    def emit_array_store(self, element_type, frame) -> str:
        """Store one array element and consume array, idx, value."""
        list(map(lambda x: frame.pop(), range(3)))
        if is_bool_type(element_type):
            return "\tbastore\n"
        elif is_int_type(element_type):
            return self.jvm.emitIASTORE()
        elif is_float_type(element_type):
            return self.jvm.emitFASTORE()
        elif is_reference_type(element_type):
            return self.jvm.emitAASTORE()
        raise IllegalOperandException(f"Unsupported array element type: {type(element_type)}")

    def emit_new_array(self, element_type, frame, ref: str | None = None) -> str:
        """Allocate an array while preserving the stack height of its size."""
        if is_int_type(element_type):
            return self.jvm.emitNEWARRAY("int")
        elif is_float_type(element_type):
            return self.jvm.emitNEWARRAY("float")
        elif is_bool_type(element_type):
            return self.jvm.emitNEWARRAY("boolean")
        elif is_string_type(element_type):
            return self.jvm.emitANEWARRAY("java/lang/String")
        elif is_struct_type(element_type):
            struct_name = ( ref
                if ref is not None else element_type.name
                if hasattr(element_type, 'name') else element_type.struct_name
            )
            if isinstance(struct_name, Id):
                struct_name = struct_name.name
            return self.jvm.emitANEWARRAY(str(struct_name))
        elif is_array_type(element_type):
            return self.jvm.emitANEWARRAY(
                ref or self.get_jvm_type(element_type)
            )
        raise IllegalOperandException(f"Unsupported array element type: {type(element_type)}")

    # -------------------------------------------
    # Operations and comparisons
    # -------------------------------------------
    def emit_if_icmpeq(self, label: int, frame) -> str:
        """Branch when two integer-like operands are equal."""
        frame.pop()
        frame.pop()
        return self.jvm.emitIFICMPEQ(label)

    def emit_if_icmpge(self, label: int, frame) -> str:
        """Branch when the left integer is greater than or equal to the right."""
        frame.pop()
        frame.pop()
        return self.jvm.emitIFICMPGE(label)

    def emit_neg_op(self, in_, frame) -> str:
        """
        Generate ineg, fneg.

        Args:
            in_: The type of the operands
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        if is_int_type(in_):
            return self.jvm.emitINEG()
        elif is_float_type(in_):
            return self.jvm.emitFNEG()
        raise IllegalOperandException(f"Unsupported negation type: {type(in_)}")

    def emit_add_op(self, lexeme: str, in_, frame) -> str:
        """
        Generate iadd, isub, fadd or fsub.

        Args:
            lexeme: The lexeme of the operator
            in_: The type of the operands
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        if lexeme == "+":
            return (self.jvm.emitIADD()
               if is_int_type(in_) else self.jvm.emitFADD()
            )
        return (self.jvm.emitISUB()
            if is_int_type(in_) else self.jvm.emitFSUB()
        )

    def emit_mul_op(self, lexeme: str, in_, frame) -> str:
        """
        Generate imul, idiv, fmul or fdiv.

        Args:
            lexeme: The lexeme of the operator
            in_: The type of the operands
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        if lexeme == "*":
            return (self.jvm.emitIMUL()
                if is_int_type(in_) else self.jvm.emitFMUL()
            )
        return (self.jvm.emitIDIV()
            if is_int_type(in_) else self.jvm.emitFDIV()
        )

    def emit_mod(self, frame) -> str:
        """
        Emit modulo instruction.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        return self.jvm.emitIREM()

    def emit_iinc(self, index: int, amount: int, frame) -> str:
        """
        Emit IINC instruction to increment/decrement a local int variable in-place.

        This instruction operates directly on the local variable table,
        NOT on the operand stack, so no push/pop is needed.

        Args:
            index: The index of the local variable
            amount: The amount to increment (negative for decrement)
            frame: Frame object (unused for stack, kept for consistency)

        Returns:
            Generated JVM instruction string
        """
        return self.jvm.emitIINC(index, amount)


    def emit_and_op(self, frame) -> str:
        """
        Generate iand for logical AND.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        return self.jvm.emitIAND()

    def emit_or_op(self, frame) -> str:
        """
        Generate ior for logical OR.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        return self.jvm.emitIOR()

    @staticmethod
    def _restore_stack(frame, target_size: int) -> None:
        """Restore one control-flow branch to the shared merge height."""
        curr_size = frame.get_stack_size()
        if curr_size < target_size:
            list(map(
                lambda x: frame.push(), range(target_size - curr_size),
            ))
        elif curr_size > target_size:
            list(map(
                lambda x: frame.pop(), range(curr_size - target_size),
            ))

    def emit_re_op(self, op: str, in_, frame) -> str:
        """
        Emit relational operation (returns int: 0 for false, non-zero for true).

        Args:
            op: Operator string (==, !=, <, <=, >, >=)
            in_: Type of operands
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        result = []
        label_f = frame.get_new_label()
        label_o = frame.get_new_label()
        frame.pop()
        frame.pop()

        if is_int_type(in_) or is_bool_type(in_):
            branches = {
                ">" : self.jvm.emitIFICMPLE,
                ">=": self.jvm.emitIFICMPLT,
                "<" : self.jvm.emitIFICMPGE,
                "<=": self.jvm.emitIFICMPGT,
                "!=": self.jvm.emitIFICMPEQ,
                "==": self.jvm.emitIFICMPNE,
            }
            result.append(branches[op](label_f))
        elif is_reference_type(in_):
            result.append(
                self.jvm.emitIFACMPNE(label_f)
                if op == "==" else self.jvm.emitIFACMPEQ(label_f)
            )
        else:
            result.append("\tfcmpg\n"
                if op in ("<", "<=") else self.jvm.emitFCMPL()
            )
            branches = {
                ">" : self.jvm.emitIFLE,
                ">=": self.jvm.emitIFLT,
                "<" : self.jvm.emitIFGE,
                "<=": self.jvm.emitIFGT,
                "!=": self.jvm.emitIFEQ,
                "==": self.jvm.emitIFNE,
            }
            result.append(branches[op](label_f))

        branch_stack = frame.get_stack_size()
        result.append(self.emit_push_iconst(1, frame))
        result.append(self.emit_goto(label_o, frame))
        self._restore_stack(frame, branch_stack)
        result.append(self.emit_label(label_f, frame))
        result.append(self.emit_push_iconst(0, frame))
        result.append(self.emit_label(label_o, frame))
        return "".join(result)

    # -------------------------------------------
    # Directives
    # -------------------------------------------
    def emit_method(self, lexeme: str, in_type, is_static: bool, desc: str | None = None) -> str:
        """
        Generate the method directive for a function.

        Args:
            lexeme: The name of the method
            in_type: The type descriptor of the method
            is_static: True if the method is static; false otherwise

        Returns:
            Generated method directive string
        """
        return self.jvm.emitMETHOD(lexeme, desc or self.get_jvm_type(in_type), is_static)

    def emit_field(self, name: str, in_, desc: str | None = None) -> str:
        """Emit a public JVM instance-field declaration."""
        return (f".field public {name} " f"{desc or self.get_jvm_type(in_)}\n")

    def emit_end_method(self, frame) -> str:
        """
        Generate the end directive for a function.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated end method directive string
        """
        buffer = []
        buffer.append(self.jvm.emitLIMITSTACK(frame.get_max_op_stack_size()))
        buffer.append(self.jvm.emitLIMITLOCAL(frame.get_max_index()))
        buffer.append(self.jvm.emitENDMETHOD())
        return "".join(buffer)

    # -------------------------------------------
    # Control flow and stack operations
    # -------------------------------------------
    def emit_if_true(self, label: int, frame) -> str:
        """
        Generate code to jump to label if the value on top of operand stack is true (non-zero).

        Args:
            label: The label where the execution continues if the value on top of stack is true
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        return self.jvm.emitIFGT(label)

    def emit_if_false(self, label: int, frame) -> str:
        """
        Generate code to jump to label if the value on top of operand stack is false (zero).

        Args:
            label: The label where the execution continues if the value on top of stack is false
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        return self.jvm.emitIFLE(label)

    def emit_dup(self, frame) -> str:
        """
        Generate code to duplicate the value on the top of the operand stack.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.push()
        return self.jvm.emitDUP()

    def emit_dup_x1(self, frame) -> str:
        """
        Generate code to duplicate the value and insert below the second stack entry.
        Stack: [..., value2, value1] -> [..., value1, value2, value1]

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.push()
        return self.jvm.emitDUPX1()

    def emit_dup_x2(self, frame) -> str:
        """
        Generate code to duplicate the value below two stack entries.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.push()
        return self.jvm.emitDUPX2()

    def emit_pop(self, frame) -> str:
        """
        Emit POP instruction.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.pop()
        return self.jvm.emitPOP()

    def emit_i2f(self, frame) -> str:
        """
        Generate code to convert an integer on top of stack to a floating-point number.

        Args:
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        return self.jvm.emitI2F()

    def emit_return(self, in_, frame) -> str:
        """
        Generate code to return.

        Args:
            in_: The type of the returned expression
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        if is_int_type(in_) or is_bool_type(in_):
            frame.pop()
            return self.jvm.emitIRETURN()
        elif is_float_type(in_):
            frame.pop()
            return self.jvm.emitFRETURN()
        elif is_void_type(in_):
            return self.jvm.emitRETURN()
        elif is_reference_type(in_):
            frame.pop()
            return self.jvm.emitARETURN()
        else:
            raise IllegalOperandException(f"Unsupported return type: {type(in_)}")

    # -------------------------------------------
    # Objects and file output
    # -------------------------------------------
    def emit_new(self, lexeme: str, frame) -> str:
        """
        Emit NEW instruction for creating struct instances.

        Args:
            lexeme: Struct name
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        frame.push()
        return self.jvm.emitNEW(lexeme)

    def emit_new_instance(self, class_name: str, frame) -> str:
        """
        Emit code to create a new instance of a class and call its constructor.
        Equivalent to: new ClassName; dup; invokespecial ClassName/<init>()V

        After this, the stack has the initialized object reference.

        Args:
            class_name: Class name (e.g., "Point")
            frame: Frame object for stack management

        Returns:
            Generated JVM instruction string
        """
        code = ""
        # new ClassName - pushes uninitialized object ref
        frame.push()
        code += self.jvm.emitNEW(class_name)
        # dup - duplicate the object ref (one for init, one to keep)
        frame.push()
        code += self.jvm.emitDUP()
        # invokespecial ClassName/<init>()V - consumes one ref
        frame.pop()
        code += self.jvm.emitINVOKESPECIAL(class_name + "/<init>", "()V")
        # Stack now has one initialized object reference
        return code

    def emit_label(self, label: int, frame) -> str:
        """
        Generate code that represents a label.

        Args:
            label: The label
            frame: Frame object for stack management

        Returns:
            Generated label code
        """
        return self.jvm.emitLABEL(label)

    def emit_goto(self, label: int, frame) -> str:
        """
        Generate code to jump to a label.

        Args:
            label: The label
            frame: Frame object for stack management

        Returns:
            Generated goto instruction string
        """
        return self.jvm.emitGOTO(label)

    def emit_prolog(self, name: str) -> str:
        """
        Generate starting directives for MiniRust program (single class with all functions).

        Args:
            name: Class name (usually "MiniRust" or "Main")

        Returns:
            Generated prolog directives string
        """
        result = []
        result.append(self.jvm.emitSOURCE(name + ".java"))
        result.append(self.jvm.emitCLASS("public " + name))
        result.append(self.jvm.emitSUPER("java/lang/Object"))
        return "".join(result)

    def emit_epilog(self) -> None:
        with open(self.filepath, "w") as file:
            file.write("".join(self.buff))

    def print_out(self, in_: str) -> None:
        """
        Print out the code to screen (add to buffer).

        Args:
            in_: The code to be printed out
        """
        self.buff.append(in_)

    def clear_buff(self) -> None:
        """
        Clear the code buffer.
        """
        self.buff.clear()

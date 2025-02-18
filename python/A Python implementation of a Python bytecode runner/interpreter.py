from dis import Bytecode, Instruction, dis
from types import ModuleType


class Scope:
    def __init__(self, func, vm: "VM") -> None:
        if isinstance(func, ModuleType):
            assert False
        self.code = Bytecode(func)
        self.vm = vm
        self.stack = []
        dis(func)

    @property
    def consts(self): return self.code.codeobj.co_consts

    def run(self, args: list):
        vm = self.vm
        vm.scope_idx += 1
        scope_idx = vm.scope_idx
        self.vars = args

        self.p = 0
        prog = list(iter(self.code))
        try:
            while self.p < len(prog):
                inst = prog[self.p]
                opname = inst.opname
                # print(self.p*2, opname)
                if opname.lower() not in vm.instructions:
                    print("*"*10)
                    print("Invalid inst", self.p*2, opname)
                    print(inst)
                    print("*"*10)
                    vm.print_stack()
                    exit(-1)
                func = vm.instructions[opname.lower()]
                last_result = func(inst)
                self.p += 1

                if opname.lower() == "return_value":
                    return last_result
        except Exception as e:
            # only this scope prints
            if scope_idx == vm.scope_idx:
                print("*"*10)
                print(
                    f"Scope idx {vm.scope_idx},\n Instruction at {self.p}, {self.p*2}")
                print(inst)
                print("*"*10)
            raise e
        vm.scope_idx -= 1

        return last_result


class VM:
    # see: https://docs.python.org/3/library/dis.html
    def __init__(self, func, globals: dict[str]) -> None:
        self.globals = globals
        self.func = func
        self.scope_idx = 0
        self.instructions = {v.__name__: v for v in {
            self.load_fast,
            self.binary_add,
            self.return_value,
            self.load_const,
            self.compare_op,
            self.pop_jump_if_false,
            self.binary_multiply,
            self.store_fast,
            self.get_iter,
            self.for_iter,
            self.load_global,
            self.call_function,
            self.jump_absolute,
            self.inplace_add,
            self.store_global,
            self.format_value,
            self.build_const_key_map,
            self.store_subscr,
            self.binary_subscr,
            self.build_string,
            self.dup_top_two,
            self.rot_three,
            self.contains_op,
            self.is_op,
            self.build_map,
            self.jump_forward,
        }}

    def run(self, args: list):
        self.current_scope = None
        return self.run_new_scope(self.func, args)
    from typing import Callable

    @ classmethod
    def call_func(self, func: Callable, args, globals):
        vm = VM(func, globals)
        return vm.run(args)

    def load_fast(self, inst: Instruction):
        self.push(self.current_scope.vars[inst.arg])

    def binary_add(self, inst: Instruction):
        self.push(self.pop()+self.pop())

    def binary_multiply(self, inst: Instruction):
        self.push(self.pop()*self.pop())

    def return_value(self, inst: Instruction):
        return self.pop()

    def load_const(self, inst: Instruction):
        self.push(self.current_scope.consts[inst.arg])

    def compare_op(self, inst: Instruction):
        from dis import cmp_op
        op = cmp_op[inst.arg]
        ops = {
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">=": lambda a, b: a >= b,
            ">": lambda a, b: a > b,
        }
        if op not in ops:
            raise NotImplementedError(f"Invalid binary op='{op}'")
        op = ops[op]
        self.push(op(self.pop(), self.pop()))

    def pop_jump_if_false(self, inst: Instruction):
        condition = self.pop()
        if condition is False:
            self._jump(inst.argval)

    def _jump(self, i):
        self.current_scope.p = int(i // 2) - 1  # loop adds one

    def _jump_delta(self, delta):
        self._jump(self.current_scope.p*2+delta)

    def print_stack(self):
        print("*"*10, "stack", "*"*10)
        print(self.current_scope.stack)
        print("*"*27)

    def store_fast(self, inst: Instruction):
        index = inst.arg
        if index >= len(self.current_scope.vars):
            self.current_scope.vars.append(self.pop())
        else:
            self.current_scope.vars[index] = self.pop()
        # print(self.current_scope.vars)

    def get_iter(self, inst: Instruction):
        self.push(iter(self.pop()))

    def push(self, *values):
        for v in values:
            self.current_scope.stack.append(v)

    def pop(self, n=1):
        if n == 1:
            return self.current_scope.stack.pop()
        else:
            return [self.current_scope.stack.pop() for _ in range(n)][::-1]

    def for_iter(self, inst: Instruction):
        iter = self.current_scope.stack[-1]
        try:
            next_val = next(iter)
            self.push(next_val)
        except StopIteration:
            self.pop()
            self._jump(inst.argval)

    def run_new_scope(self, func, args):
        print("Calling", func.__name__, "Args", args)
        nargs = func.__code__.co_argcount
        if (nargs != len(args)):
            raise Exception(
                f"{func.__name__} takes {nargs} args, but {len(args)} were given.")

        old_scope = self.current_scope
        self.current_scope = Scope(func, self)
        ret_val = self.current_scope.run(args)
        self.current_scope = old_scope
        return ret_val

    def call_function(self, inst: Instruction):
        argcount = inst.arg
        self.print_stack()
        args = self.pop(argcount)
        if argcount == 1:
            args = (args,)
        func = self.pop()
        if func.__name__ in __builtins__:
            val = func(*args)
        else:
            val = self.run_new_scope(func, args)
        self.push(val)

    def load_global(self, inst: Instruction):
        # ???
        name = inst.argval
        if name in __builtins__:
            val = __builtins__[name]
        else:
            val = self.globals[name]
        self.push(val)

    def store_global(self, inst: Instruction):
        name = inst.argval
        assert name in self.globals
        self.globals[name] = self.pop()

    def jump_absolute(self, inst: Instruction):
        self._jump(inst.argval)

    def inplace_add(self, inst: Instruction):
        self.push(self.pop() + self.pop())

    def format_value(self, inst: Instruction):
        type = inst.arg
        if type == 0:
            self.push(str(self.pop(1)))
        else:
            raise NotImplementedError("format_value {type}")

    def build_string(self, inst: Instruction):
        n = inst.arg
        self.push("".join(self.pop(n)))

    def build_const_key_map(self, inst: Instruction):
        n = inst.arg
        keys = self.pop()
        assert n == len(keys)
        values = self.pop(n)
        self.push({k: v for k, v in zip(keys, values)})

    def store_subscr(self, inst: Instruction):
        value, dict, key = self.pop(3)
        dict[key] = value

    def binary_subscr(self, inst: Instruction):
        dict, key = self.pop(2)
        self.push(dict[key])

    def _dup_top(self, n):
        top = self.pop(n)
        self.push(*top)
        self.push(*top)

    def dup_top_two(self, inst: Instruction):
        self._dup_top(2)

    def rot_three(self, inst: Instruction):
        i1, i2, i3 = self.pop(3)
        self.push(i3, i1, i2)

    def contains_op(self, inst: Instruction):
        item, l = self.pop(2)
        val = item in l
        if inst.arg == 1:
            val = not val
        self.push(val)

    def is_op(self, inst: Instruction):
        item1, item2 = self.pop(2)
        val = item1 is item2
        if inst.arg == 1:
            val = not val
        self.push(val)

    def build_map(self, inst: Instruction):
        count = inst.arg
        dict = {}
        for _ in range(count):
            k, v = self.pop(2)
            dict[k] = v
        self.push(dict)

    def jump_forward(self, inst: Instruction):
        delta = inst.arg
        self._jump_delta(delta+2)

from collections import defaultdict
from pprint import pprint
import json


class Debugger:
    def __init__(self):
        self.commands = {
            "quit": self.quit,
            "strings": self.strings,
            "solve_coins": self.solve_coins,
            "save": self.save,
            "regs": self.regs,
            "setreg": self.setreg,
            "loadcmd": self.loadcmd,
            "debugmode": self.debugmode,
            "step": self.step,
            "run": self.run,
            "continue": self.continue_run,
            "printcommands": self.printcommands
        }

    def save(self, cpu, *args):
        """Save cpu state to <filename>."""
        state = {
            "pc": cpu.pc - 2,
            "regs": cpu.regs,
            "stack": cpu.stack,
            "memory": cpu.memory
        }
        with open(args[1], "w") as f:
            f.write(json.dumps(state))

    def debugmode(self, cpu, *args):
        """Set debugmode ON or OFF."""
        cpu.debugmode = (len(args) > 0) and (args[0].upper() == "ON")
        print(f"Debug output is now {cpu.debugmode}")

    def regs(self, cpu, *args):
        """Print registers."""
        print(cpu.regs)

    def setreg(self, cpu, *args):
        """Set register <n> to <v>."""
        reg = int(args[0])
        value = int(args[1])
        cpu.regs[reg] = value
        self.regs(cpu)

    def loadcmd(self, cpu, *args):
        "Load adventure commands."
        with open(args[0]) as f:
            cpu.next_command = [_.strip() for _ in f.readlines()]

    def printcommands(self, cpu, *args):
        """Print commands"""
        print("Commands so far\n\t", end="")
        print("\n\t".join(cpu.commands))

    def quit(self, cpu, *args):
        """quit the program"""
        print("Quitting")
        exit()

    def help(self, cpu, *args):
        print("Available commands:")
        for name, op in self.commands.items():
            doc = op.__doc__ or ""
            print(f"{name}\t\t{doc.strip()}")

    def solve_coins(self, cpu, *args):
        """Solve the coin equation."""
        args = [int(_) for _ in args]
        if len(args) != 5:
            print("You need five coins!")
            return
        for i in args:
            for j in args:
                for k in args:
                    for l in args:
                        for m in args:
                            if i + j * k**2 + l**3 - m == 399:
                                if set([i, j, k, l, m]) == set(args):
                                    print("The correct order is:", i, j, k, l, m)

    def strings(self, cpu, args):
        """Display strings in the binary file"""
        for i, m in enumerate(self.memory):
            if m[0] == 19:
                print(chr(self.memory[i+1][0]), end="")

    def step(self, cpu, *args):
        """Run in step mode"""

        cpu.paused = True if not args else args[0].upper() in ["ON", "TRUE", "YES"]
        print(f"CPU step mode {cpu.paused}.")

    def run(self, cpu, *args):
        """Run <n> steps (1 default)"""
        steps = 1 if not args else int(args[0])
        cpu.steps = steps
        # cpu.breakpoints.append(steps)
        cpu.paused = False

    def continue_run(self, cpu, *args):
        """Run (to next bp or input)."""
        cpu.steps = None
        cpu.paused = False

    def command(self, cpu, cmd: str):
        parts = cmd.split()
        if not parts:
            return
        op = self.commands.get(parts[0], self.help)
        op(cpu, *parts[1:])


class CPU():
    def dereference(self, value: int) -> int:
        if value & 0b1000_0000_0000_0000:
            return self.regs[value & 0xFF]
        return value

    def halt(self):
        self.halted = True

    def output(self):
        a = self.getnext()
        c = chr(self.dereference(a))
        self.debug(f"-> [{c}]")
        print(c, end="")

    def noop(self):
        pass

    def setreg(self):
        a = self.getnext()
        b = self.getnext()
        self.debugparams(a=a, b=b)
        self.regs[a & 0xFF] = self.dereference(b)

    def push(self):
        a = self.getnext()
        self.debugparams(a=a)
        self.stack.append(self.dereference(a))

    def pop(self):
        a = self.getnext()
        stack = self.stack.pop()
        self.debug(f"(a={a}) <= {stack}")
        self.write(a, stack)

    def eq(self):
        a = self.getnext()
        b = self.getnext()
        c = self.getnext()

        self.debugparams(a=a, b=b, c=c)
        if self.dereference(b) == self.dereference(c):
            self.write(a, 1)
        else:
            self.write(a, 0)

    def gt(self):
        a = self.getnext()
        b = self.getnext()
        c = self.getnext()
        self.debugparams(a=a, b=b, c=c)
        if self.dereference(b) > self.dereference(c):
            self.write(a, 1)
        else:
            self.write(a, 0)

    def jmp(self):
        a = self.getnext()
        self.debugparams(a=a)
        oldpc = self.pc
        self.pc = self.dereference(a)
        self.debug(f"Jumping from {oldpc} to {self.pc}.")

    def jt(self):
        a = self.getnext()
        b = self.getnext()
        self.debugparams(a=a, b=b)
        if self.dereference(a) != 0:
            self.pc = self.dereference(b)

    def jf(self):
        a = self.getnext()
        b = self.getnext()
        self.debugparams(a=a, b=b)
        if self.dereference(a) == 0:
            self.debug(f"Jumping to {b}")
            self.pc = self.dereference(b)

    def add(self):
        a = self.getnext()
        b = self.getnext()
        c = self.getnext()
        self.debugparams(a=a, b=b, c=c)
        self.write(a, (self.dereference(b) + self.dereference(c)) % 32768)

    def mul(self):
        a = self.getnext()
        b = self.getnext()
        c = self.getnext()
        self.debugparams(a=a, b=b, c=c)
        self.debug(f"== {self.dereference(b) * self.dereference(c)} -> % {self.dereference(b) * self.dereference(c) % 32768}")
        self.write(a, (self.dereference(b) * self.dereference(c)) % 32768)

    def mod(self):
        a = self.getnext()
        b = self.getnext()
        c = self.getnext()
        self.debugparams(a=a, b=b, c=c)
        self.write(a, self.dereference(b) % self.dereference(c))

    def op_and(self):
        a = self.getnext()
        b = self.getnext()
        c = self.getnext()
        self.debugparams(a=a, b=b, c=c)
        self.write(a, self.dereference(b) & self.dereference(c))

    def op_or(self):
        a = self.getnext()
        b = self.getnext()
        c = self.getnext()
        self.debugparams(a=a, b=b, c=c)
        self.debug(f"== {self.dereference(b):b} | {self.dereference(c):b} = {self.dereference(b) | self.dereference(c)}")
        self.write(a, self.dereference(b) | self.dereference(c))

    def op_not(self):
        a = self.getnext()
        b = self.getnext()
        self.debugparams(a=a, b=b)
        b = self.dereference(b)
        self.debug(f"== {b:b} -> {~b & 0b0111_1111_1111_1111:b} == {~b & 0b0111_1111_1111_1111}")
        self.write(a, ~b & 0b0111_1111_1111_1111)

    def rmem(self):
        a = self.getnext()
        b = self.getnext()
        self.debug(f"(a={a}, b={b}->{self.dereference(b)}->{self.getmem(self.dereference(b))})")
        v = self.getmem(self.dereference(b))
        self.write(a, self.dereference(v))

    def wmem(self):
        a = self.getnext()
        b = self.getnext()
        self.debugparams(a=a, b=b)
        self.write(self.dereference(a), self.dereference(b))

    def call(self):
        a = self.getnext()
        self.debugparams(a=a)
        self.stack.append(self.pc)
        self.pc = self.dereference(a)

    def ret(self):
        addr = self.stack.pop()
        self.pc = addr

    def input(self):
        a = self.getnext()
        while not self.inputbuf:
            # Allow for canned commands
            if self.next_command:
                self.inputbuf = self.next_command[0] + "\n"
                print(f"Canned command: {self.inputbuf.strip()}")
                self.next_command = self.next_command[1:]
            else:
                self.inputbuf = input("? <dbg-commands start with '.'>") + "\n"

            # If command starts with '.', send command to debugger
            if self.debugger and self.inputbuf.startswith("."):
                debugger.command(self, self.inputbuf[1:-1])
                self.commands.append(self.inputbuf.strip())
                self.inputbuf = ""

        c = self.inputbuf[:1]
        if c == "\n":
            self.commands.append(self.command.strip())
            self.command = ""
        else:
            self.command += c

        self.inputbuf = self.inputbuf[1:]
        self.write(a, ord(c))

    def __init__(self, memory: list):
        self.steps = None
        self.next_command = []
        self.memory = memory
        self.halted = False
        self.pc = 0
        self.debugmode = False
        self.regs = {i: 0 for i in range(8)}
        self.stack = []
        self.stats = defaultdict(int)
        self.breakpoints = []
        self.inputbuf = ""
        self.paused = False
        self.command = ""
        self.commands = []
        self.debugger = None
        self.ops = {
            0: self.halt,
            1: self.setreg,
            2: self.push,
            3: self.pop,
            4: self.eq,
            5: self.gt,
            6: self.jmp,
            7: self.jt,
            8: self.jf,
            9: self.add,
            10: self.mul,
            11: self.mod,
            12: self.op_and,
            13: self.op_or,
            14: self.op_not,
            15: self.rmem,
            16: self.wmem,
            17: self.call,
            18: self.ret,
            19: self.output,
            20: self.input,
            21: self.noop}

    def debug(
            self,
            s: str,
            force: bool = False,
            *,
            end: str = "\n") -> None:
        if force or self.debugmode:
            print(s, end=end)

    def debugparams(self, **args):
        if self.debugmode:
            arg_s = []
            for a, v in args.items():
                s = f"{a}={v}"
                if v & (1 << 15):
                    s += f"->{self.dereference(v)}"
                arg_s.append(s)

            self.debug(f"({', '.join(arg_s)})")

    def write(self, addr, value):
        v1 = value & 0x00FF
        v2 = (value & 0xFF00) >> 8
        if addr & (1 << 15):
            self.regs[addr & 0x00FF] = value
        else:
            self.memory[addr] = (v1, v2)

    def getmem(self, addr):
        if addr & (1 << 15):
            self.debug("REGISTRY ACCESS")
        word = self.memory[addr]
        res = word[0] ^ (word[1] << 8)

        return res

    def getnext(self):
        res = self.getmem(self.pc)
        self.pc += 1
        return res

    def execute(self):
        # self.debugmode = True
        instruction = self.getnext()
        self.stats[self.ops[instruction].__name__] += 1
        if instruction in self.ops:
            # if instruction in [20]:
            #     self.debugmode = True
            # if instruction == 19:
            #     self.debugmode = False

            self.debug(f"[{str(self.pc-1).zfill(5)}] {self.ops[instruction].__name__}", end="")
            self.ops[instruction]()
            self.debug(f"        {self.regs}")

    def run(self):
        while (not self.halted) and (self.pc < len(self.memory)):
            self.execute()
            if self.steps is not None:
                self.steps -= 1
                # print("Remaining:", self.steps)
            if self.pc in self.breakpoints or self.steps == 0:
                self.paused = True
            if self.paused:
                cmd = input("dbg <no '.'>: ")
                self.debugger.command(cpu, cmd)
                if self.steps == 0:
                    self.steps = None
        self.halted = False


def assemble(s):
    res = []
    codes = s.split(",")
    for code in [int(c) for c in codes]:
        res.append((code & 0x00FF, (code & 0xFF00) >> 8))
    return res


def load(filename: str) -> list:
    i = 0
    res = []
    with open(filename, mode="rb") as f:
        b = f.read(2)
        while b:
            res.append([_ for _ in b])
            b = f.read(2)
            i += 1
            if i % 1024 == 0:
                print(i // 1024, end="\r")
    return res


def load_state(cpu: CPU, filename: str):
    with open(filename) as f:
        state = json.loads(f.read())
        cpu.pc = state["pc"]
        cpu.regs = {int(k): v for k, v in state["regs"].items()}
        cpu.stack = state["stack"]
        cpu.memory = state["memory"]
        print(cpu.pc)
        print(cpu.regs)


def strings(cpu):
    for i, m in enumerate(cpu.memory):
        if m[0] == 19:
            print(chr(cpu.memory[i+1][0]), end="")


bin = load("challenge.bin")
# bin = assemble("9,32768,32769,4,19,32768")
cpu = CPU(bin)
debugger = Debugger()
cpu.debugger = debugger
load_state(cpu, "startgame.state")
# cpu.debugmode = True
cpu.breakpoints.append(6048)
# strings(cpu)
cpu.run()
pprint(cpu.stats)

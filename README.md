# Synacore Challenge

Having played [Advent of Code](https://adventofcode.com) since start, I was very pleased to learn about the [Synacore Challenge](https://challenge.synacor.com/).

In essence you sign up, get a description for a CPU architecture and a bin-file and then all you have to do is implement the emulator and run the bin-file.

From here on it will be a lot of spoilers, so you may want to wait with reading all of the text until you've solved the puzzles or need help. Scoring 100% on the exam is easy if you have the answer cheat sheet, but it is not nearly as fun :)

# Emulator implementation

With the emulator implemented, load the bin-file into memory and run it. You'll get a startup message and then it runs [POST](https://en.wikipedia.org/wiki/Power-on_self-test).

For me, it said stuff like "no gt op", "no rmem op" etc. That baffled me, as I had implemented all the operations. Indeed, but the POST checks if they are implemented correctly.

It took me a while to get the last ones right (rmem, wmem), mainly due to not reading carefully enough when and what to dereference. As you get from the instructions, memory is 15 bit, and if the 16th bit is set, reading is not from RAM but from a register. Pay close attention to that part!

While trying to figure out what was wrong with my code I added a lot of debug output. This is not a waste of time, as it will come in handy later - and probably much more than you implemented at this stage.

# Adventure game

With the computer fully operatioonal you are thrown into a text based adventure game, Zork-style. Wow! The main challenge here is to find the way around the maze on the lowest level.

# Coins

Solving the riddle with the coins is straight-forward. In my debugger I added `.solve-coins <n> <n> <n> <n> <n>` as a helper function just for fun.

# Teleporter

This is where you need a more powerful debugger. To me this is the hardest problem so far. The gist of it is to
* Set a register to a teleporter-friendly value.
* Disassemble the validation code to understand what a 'teleporter-friendly value' is.
* Patch the binary to skip the validation.

## Debugger
```
? <dbg-commands start with '.'>.help
Available commands:
quit            quit the program
strings         Display strings in the binary file
solve_coins             Solve the coin equation.
save            Save cpu state to <filename>.
regs            Print registers.
setreg          Set register <n> to <v>.
loadcmd         Load adventure commands.
debugmode               Set debugmode ON or OFF.
step            Run in step mode
run             Run <n> steps (1 default)
continue                Run (to next bp or input).
printcommands           Print commands
```

So I built a debugger, with a fairly easy mechanism to plug in new commands. This is totally over-engineered, and the reason for that is that I have no real idea what to do next.

My game plan is as follows:
* Run the game to where I have the teleporter (either by restoring state or playing is using the canned script).
* Set reg 8 to some random value
* Turn on debug output
* Run a few thousand instructions
* Find loops and try to convert the assembler to something comprehensible :)

I believe there are take-off/landing zones with `noop` that I can patch and jump to/from - once I have figured out what the correct value of reg 8 is.

When I added a [`.strings`](https://linux.die.net/man/1/strings) command I thought maybe it'd be simple to extract all text in the game. However, that is not exactly the case, as most of the text is encrypted.

I believe it might be simpler to crack the text encryption assembler, and extract all text to see the codes.

Another idea is to disassemble the whole thing and try to trace code...
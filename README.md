# Dialogue Designer importer
A Python3 implementation of an importer for [Dialogue Designer](https://radmatt.itch.io/dialogue-designer) from [radmatt](https://radmatt.itch.io/).

An important note: this library provides no graphical implementation of a
dialogue system. Its purpose is solely to help importing and managing
files exported from Dialogue Designer (DD from now on). This project exists
so that you don't have to manually import the json in a dict and implement
all the different node behaviours manually.

## Usage
To import a file exported from Dialogue Designer, everything you need to do is:
```py
import ddesigner

data = ddesigner.from_file(open('exported_file.json'))
dial = ddesigner.Dialogue(data)
```

The imported data is saved in a `DialogueData` class, which is to be considered
immutable. The `Dialogue` instance that we create to manage it is a state machine
that encapsulates the data and let us work on it freely.

The `Dialogue` instance can be used to programmatically access and modify
variables set in the DD editor:
```py
# ...

dial['var1'] = 10
```

Variables internal to a dialogue will be used for node computation. In fact,
most of the behaviour of nodes are automated.

Imagine a DD export with this sequence of nodes:
```
start -> show message -> condition (var1 > 0) -True-> set variable (var2 = "goofy")
                                |
                                | False
                                v
                         set variable (var2 = "mickey")
```

We can cycle through the state machine using our `Dialogue` instance:
```py
# ...

dial['var1'] = 10

print(dial.next_iter())     # Prints the node info: {... , 'text': {'ENG': '...'}}
                            # The 'text' field can be used to populate on screen a
                            # dialogue box.
print(dial.next_iter())     # Prints: None
                            # This is because the condition and set variable nodes
                            # are executed silently, trying to reach a new
                            # blocking point (eg. a show message). Since no
                            # blocking point is found, the dialogue iters till
                            # the end, giving None as a final result (no more
                            # nodes to process).

# All the nodes have fulfilled their duty at this point. Since we
# set 'var1' to 10, and the condition checks for var1 > 0 we can
# expect to find that var2 set to "goofy" (the True branch for the condition
# node).
print(dial['var2'])         # Prints: goofy
```

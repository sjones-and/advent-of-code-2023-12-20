#!/usr/bin/env python3

import os
from time import perf_counter_ns
from math import lcm

class Module:
    EventQueue = []
    HighCount = 0
    LowCount = 0
    Modules = {}
    Patterns = {}

    def create(data):
        module_info = data.split(' ')[0].strip()
        if module_info == 'broadcaster':
            Module.Modules[module_info] = Broadcaster()
        elif module_info[0] == '%':
            Module.Modules[module_info[1:]] = FlipFlop(module_info[1:])
        elif module_info[0] == '&':
            Module.Modules[module_info[1:]] = Conjunction(module_info[1:])
        else:
            assert(False)

    def wire_up(data):
        source_module_name = data.split(' ')[0].strip().strip('&%')
        target_module_names = map(lambda x: x.strip(), data.split('>')[1].strip().split(','))
        source_module = Module.Modules[source_module_name]
        for target_module_name in target_module_names:
            source_module.feeds.append(target_module_name)
            if target_module := Module.Modules.get(target_module_name, None):
                source_module += target_module.register_input()
            else:
                Module.Modules[target_module_name] = Output()
                source_module += Module.Modules[target_module_name].register_input()
                               
    def __init__(self, name):
        self.__eventhandler = []
        self.name = name
        self.feeds = []

    def __iadd__(self, Ehandler): 
        self.__eventhandler.append(Ehandler) 
        return self

    def __isub__(self, Ehandler): 
        self.__eventhandler.remove(Ehandler) 
        return self

    def __call__(self, value): 
        for __eventhandler in self.__eventhandler: 
            Module.EventQueue.append((__eventhandler, value))

    def record(self, value):
        if value:
            Module.Patterns[self.name] = counter

    def process():
        if Module.EventQueue:
            events = [event for event in Module.EventQueue]
            Module.EventQueue = []
            while event := events.pop(0) if events else False:
                if event[1]:
                    Module.HighCount += 1
                else:
                    Module.LowCount += 1
                event[0](event[1])
        return len(Module.EventQueue) > 0
    
class FlipFlop(Module):
    def __init__(self, name):
        super().__init__(name)
        self.output = False
    
    def set_input(self, input):
        if not input:
            self.output = not self.output
            self(self.output)

    def register_input(self):
        return self.set_input

class Conjunction(Module):
    def __init__(self, name):
        super().__init__(name)
        self.inputs = []
        self.output = True

    def register_input(self):
        index = len(self.inputs)
        self.inputs.append(False)
        return lambda x: self.set_input(index, x)

    def set_input(self, index, input):
        self.inputs[index] = input
        self.output = not(all(self.inputs))
        self(self.output)

class Broadcaster(Module):
    def __init__(self):
        super().__init__('broadcaster')
        self.output = None
    
    def set_input(self, input):
        self.output = input
        self(self.output)

    def register_input(self):
        return self.set_input

class Button(Module):
    def __init__(self):
        super().__init__('button')
        self.output = None

    def press(self):
        self.output = False
        self(self.output)

class Output:
    def __init__(self):
        self.value = None
        self.feeds = []

    def set_input(self, value):
        if not value:
            print('JACKPOT')
        self.value = value

    def register_input(self):
        return self.set_input

def answer(input_file):
    start = perf_counter_ns()
    with open(input_file, 'r') as input_stream:
        data = input_stream.read().split('\n')

    for module in data:
        Module.create(module)

    for module in data:
        Module.wire_up(module)

    feeders = ['rx']
    while len(feeders) <= 1:
        feeders = [name for name, module in Module.Modules.items() if feeders[0] in module.feeds]

    for feeder in feeders:
        Module.Modules[feeder] += Module.Modules[feeder].record
        Module.Patterns[feeder] = None

    button = Button()
    button += Module.Modules['broadcaster'].register_input()
    global counter
    counter = 0
    while True:
        counter += 1
        button.press()
        while(Module.process()):
            pass
        if counter % 100 == 0:
            if all(Module.Patterns.values()):
                answer = lcm(*Module.Patterns.values())
                break

    end = perf_counter_ns()

    print(f'The answer is: {answer}')
    print(f'{((end-start)/1000000):.2f} milliseconds')

input_file = os.path.join(os.path.dirname(__file__), 'input')
answer(input_file)

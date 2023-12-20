#!/usr/bin/env python3

import os
from time import perf_counter_ns

class Module:
    EventQueue = []
    HighCount = 0
    LowCount = 0
    Modules = {}

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
            if target_module := Module.Modules.get(target_module_name, None):
                source_module += target_module.register_input()
            else: 
                Module.Modules[target_module_name] = Output()
                source_module += Module.Modules[target_module_name].register_input()
                               
    def __init__(self, name):
        self.__eventhandler = []
        self.name = name

    def __iadd__(self, Ehandler): 
        self.__eventhandler.append(Ehandler) 
        return self

    def __isub__(self, Ehandler): 
        self.__eventhandler.remove(Ehandler) 
        return self

    def __call__(self, value): 
        for __eventhandler in self.__eventhandler: 
            Module.EventQueue.append((__eventhandler, value))

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
        pass

    def register_input(self):
        return lambda x: None

def answer(input_file):
    start = perf_counter_ns()
    with open(input_file, 'r') as input_stream:
        data = input_stream.read().split('\n')

    for module in data:
        Module.create(module)

    for module in data:
        Module.wire_up(module)

    button = Button()

    button += Module.Modules['broadcaster'].register_input()

    for _ in range(1000):
        button.press()
        while(Module.process()):
            pass

    answer = Module.LowCount * Module.HighCount
    end = perf_counter_ns()

    print(f'The answer is: {answer}')
    print(f'{((end-start)/1000000):.2f} milliseconds')

input_file = os.path.join(os.path.dirname(__file__), 'input')
answer(input_file)

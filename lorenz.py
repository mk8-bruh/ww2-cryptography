from __future__ import annotations
from winter import *
from math import floor, ceil
from re import finditer

def wrap(sequence: str|list|tuple, length: int):
    return [sequence[i: i + length] for i in range(0, len(sequence), length)]

def wordWrap(text: str, width: int):
    paragraphs = text.split("\n")
    lines = []
    for p in paragraphs:
        lines += [""] if p == "" else wrap(p, width)
    return lines

# Baudot code implementation
BAUDOT = {
    'A': '11000',
    'B': '10011',
    'C': '01110',
    'D': '10010',
    'E': '10000',
    'F': '10110',
    'G': '01011',
    'H': '00101',
    'I': '01100',
    'J': '11010',
    'K': '11110',
    'L': '01001',
    'M': '00111',
    'N': '00110',
    'O': '00011',
    'P': '01101',
    'Q': '11101',
    'R': '01010',
    'S': '10100',
    'T': '00001',
    'U': '11100',
    'V': '01111',
    'W': '11001',
    'X': '10111',
    'Y': '10101',
    'Z': '10001',
    ' ': '00100',
    '!': '00000', # NULL
    '^': '00010', # CR
    '$': '01000', # LF
    '#': '11011', # FIGURE SHIFT
    '@': '11111', # LETTER SHIFT
}

BAUDOT_REV = {v:k for k,v in BAUDOT.items()}

class LorenzWheel:
    def __init__(self, size: int, pins: str = None, position: int = 0, name: str = None):
        self.size = size
        self.pins = [0] * size if pins is None else [int(c) for c in pins]
        self.position = position
        self.name = name
    
    def step(self):
        self.position = (self.position + 1) % self.size
    
    def current_pin(self):
        return self.pins[self.position]
    
    def set_pin(self, value: int):
        self.pins[self.position] = value
    
    def set_position(self, pos: int):
        if 0 <= pos < self.size:
            self.position = pos

class LorenzSZ:
    def __init__(self):
        # Chi wheels (5 wheels)
        self.chi_wheels = [
            LorenzWheel(41, name="χ1"),
            LorenzWheel(31, name="χ2"),
            LorenzWheel(29, name="χ3"),
            LorenzWheel(26, name="χ4"),
            LorenzWheel(23, name="χ5")
        ]
        # Psi wheels (5 wheels)
        self.psi_wheels = [
            LorenzWheel(43, name="ψ1"),
            LorenzWheel(47, name="ψ2"),
            LorenzWheel(51, name="ψ3"),
            LorenzWheel(53, name="ψ4"),
            LorenzWheel(59, name="ψ5")
        ]
        # Motor wheels (2 wheels)
        self.motor_wheels = [
            LorenzWheel(37, name="M37"),
            LorenzWheel(61, name="M61")
        ]
        self.current_wheel_set = "chi"  # "chi", "psi", or "motor"
        self.selected_wheel = 0
        self.plaintext = ""
        self.ciphertext = ""
        self.scroll = 0
    
    def step_wheels(self):
        # Step all wheels (simplified stepping)
        for (i, wheel) in enumerate(self.chi_wheels):
            wheel.step()
        for (i, wheel) in enumerate(self.psi_wheels):
            if self.motor_wheels[0].current_pin() == 1:
                wheel.step()
        for (i, wheel) in enumerate(self.motor_wheels):
            if i + 1 >= len(self.motor_wheels) or self.motor_wheels[i + 1].current_pin() == 1:
                wheel.step()
    
    def encrypt_char(self, char: str):
        if char not in BAUDOT:
            return char
        
        # Get current pins from all wheels
        chi_bits = [wheel.current_pin() for wheel in self.chi_wheels]
        psi_bits = [wheel.current_pin() for wheel in self.psi_wheels]
        
        # Convert character to Baudot
        baudot = BAUDOT[char]
        encrypted = ""

        # XOR all bits
        for i in range(5):
            chi = chi_bits[i]
            psi = psi_bits[i]
            psi = (0 if psi else 1) # invert psi
            original_bit = int(baudot[i])
            encrypted += str(original_bit ^ chi ^ psi)
        
        return BAUDOT_REV.get(encrypted, '?')
    
    def process_char(self, char: str):
        if char in BAUDOT:
            encrypted = self.encrypt_char(char.upper())
            self.plaintext += char
            self.ciphertext += encrypted
            self.step_wheels()
        elif char == '\n':
            self.plaintext += char
            self.ciphertext += char
        self.scroll = -1

# Interface
window = Program(41, 13, "LORENZ SZ", killKey="escape")

class Main(ProgramState):
    def __init__(self):
        self.machine = LorenzSZ()
        self.mode = "text"  # "text" or "wheels"
        self.edit_mode = "pins"  # "pins" or "jump"
        self.jump_buffer = ""
        self.scroll = 0

        self.wheel_stack = []

    def Keypress(self, key):
        if self.mode == "text":
            if key == "up":
                self.scroll -= 1
            elif key == "down":
                self.scroll += 1
            elif key == "backspace":
                if len(self.machine.plaintext) > 0:
                    if self.machine.plaintext[-1] != '\n' and len(self.wheel_stack) > 0:
                        (chi, psi, motor) = self.wheel_stack.pop()
                        for (i, p) in enumerate(chi):
                            self.machine.chi_wheels[i].position = p
                        for (i, p) in enumerate(psi):
                            self.machine.psi_wheels[i].position = p
                        for (i, p) in enumerate(motor):
                            self.machine.motor_wheels[i].position = p
                    self.machine.plaintext = self.machine.plaintext[:-1]
                    self.machine.ciphertext = self.machine.ciphertext[:-1]
                self.scroll = -1
            elif key == "tab":
                self.mode = "wheels"
            elif key == "enter":
                self.machine.process_char("\n")
                self.scroll = -1
            else:
                key = " " if key == "space" else key.upper()
                if key in BAUDOT:
                    self.wheel_stack.append((tuple(w.position for w in self.machine.chi_wheels), tuple(w.position for w in self.machine.psi_wheels), tuple(w.position for w in self.machine.motor_wheels)))
                    self.machine.process_char(key)
                    self.scroll = -1
        
        elif self.mode == "wheels":
            wheel_set = self.machine.current_wheel_set
            wheels = []
            if wheel_set == "chi":
                wheels = self.machine.chi_wheels
            elif wheel_set == "psi":
                wheels = self.machine.psi_wheels
            else:
                wheels = self.machine.motor_wheels
            
            selected_wheel = self.machine.selected_wheel
            current_wheel = wheels[selected_wheel]
            
            if key == "left":
                self.jump_buffer = ""
                if selected_wheel > 0:
                    self.machine.selected_wheel -= 1
                else:
                    # Cycle wheel sets: motor -> psi -> chi -> motor
                    if wheel_set == "chi":
                        self.machine.current_wheel_set = "motor"
                        wheels = self.machine.motor_wheels
                        self.machine.selected_wheel = len(wheels) - 1
                    elif wheel_set == "psi":
                        self.machine.current_wheel_set = "chi"
                        wheels = self.machine.chi_wheels
                        self.machine.selected_wheel = len(wheels) - 1
                    else:  # motor
                        self.machine.current_wheel_set = "psi"
                        wheels = self.machine.psi_wheels
                        self.machine.selected_wheel = len(wheels) - 1
            elif key == "right" or key == "enter":
                self.jump_buffer = ""
                if selected_wheel < len(wheels) - 1:
                    self.machine.selected_wheel += 1
                else:
                    # Cycle wheel sets: chi -> psi -> motor -> chi
                    if wheel_set == "chi":
                        self.machine.current_wheel_set = "psi"
                        wheels = self.machine.psi_wheels
                        self.machine.selected_wheel = 0
                    elif wheel_set == "psi":
                        self.machine.current_wheel_set = "motor"
                        wheels = self.machine.motor_wheels
                        self.machine.selected_wheel = 0
                    else:  # motor
                        self.machine.current_wheel_set = "chi"
                        wheels = self.machine.chi_wheels
                        self.machine.selected_wheel = 0
            elif key == "up":
                current_wheel.position = (current_wheel.position - 1) % current_wheel.size
                self.edit_mode = "pins"  # Exit jump mode when manually moving
                self.jump_buffer = ""
            elif key == "down":
                current_wheel.position = (current_wheel.position + 1) % current_wheel.size
                self.edit_mode = "pins"  # Exit jump mode when manually moving
                self.jump_buffer = ""
            elif key == "space":
                self.jump_buffer = ""
                if   self.edit_mode == "pins":
                     self.edit_mode =  "jump"
                elif self.edit_mode == "jump":
                     self.edit_mode =  "pins"
            elif key == "tab":
                self.mode = "text"
                self.scroll = -1
                # Reset jump state when leaving wheel mode
                self.edit_mode = "pins"
                self.jump_buffer = ""
            elif self.edit_mode == "pins":
                if key in ("0", "1"):
                    current_wheel.set_pin(int(key))
                    current_wheel.position = (current_wheel.position + 1) % current_wheel.size
            elif self.edit_mode == "jump":
                if key.isdigit():
                    self.jump_buffer += key
                    new_pos = int(self.jump_buffer) - 1
                    if 0 <= new_pos < current_wheel.size:
                        current_wheel.position = new_pos
                    else:
                        self.jump_buffer = self.jump_buffer[:-1]
                    if int(self.jump_buffer + "0") > current_wheel.size:
                        self.jump_buffer = ""
                        if self.machine.selected_wheel < len(wheels) - 1:
                            self.machine.selected_wheel += 1
                        else:
                            self.machine.selected_wheel = 0
                            self.edit_mode = "pins"
        
        lines = wordWrap(self.machine.plaintext + ("_" if self.mode == "text" else ""), 20)
        self.scroll = max(0, min(len(lines) - 5, self.scroll) if self.scroll >= 0 else len(lines) - 5)
        
        self.Draw()

    def Enter(self, prev):
        window.Clear()
        Terminal.ResetStyle()
        Terminal.SetCursorPosition(0, 1)
        Terminal.Print(
'''
║                                         ║
║                                         ║
║>----------------------------------------║
║                                         ║
║                                         ║
║                                         ║
║-----------------------------------------║
║    [plaintext]     |    [ciphertext]    ║
║                    |                    ║
║                    |                    ║
║                    |                    ║
║                    |                    ║
║                    |                    ║
'''[1:-1]
        )
        self.Draw()
    
    def Draw(self):
        Terminal.ResetStyle()
        
        # Draw wheel editor
        wheel_set = self.machine.current_wheel_set
        wheels = []
        if wheel_set == "chi":
            wheels = self.machine.chi_wheels
        elif wheel_set == "psi":
            wheels = self.machine.psi_wheels
        else:
            wheels = self.machine.motor_wheels
        
        selected_wheel = self.machine.selected_wheel
        for row in range(5):
            Terminal.SetCursorPosition(2, 1 + row)
            for i, wheel in enumerate(wheels):
                pos = wheel.position
                # Display 3 pins: previous, current, next
                prev_pin = wheel.pins[(pos - 1) % wheel.size]
                curr_pin = wheel.pins[pos]
                next_pin = wheel.pins[(pos + 1) % wheel.size]
                
                # Highlight current wheel and current pin
                is_selected_wheel = (i == selected_wheel)
                is_center_pin = (row == 2)
                
                pin_str = ""

                # Apply styling
                if self.mode == "wheels" and is_selected_wheel:
                    pin_str += Terminal.SetColor("yellow", gen = True)
                    if is_center_pin and self.edit_mode == "pins":
                        pin_str += Terminal.EnableStyle("invert", gen = True)
                
                # Pin display
                if row == 0:
                    pin_str += f"{wheel.name}"
                elif row == 1:
                    pin_str += f"{prev_pin}"
                elif row == 2:
                    pin_str += f"{curr_pin:^3}"
                elif row == 3:
                    pin_str += f"{next_pin}"
                elif row == 4:
                    pin_str += f"{self.jump_buffer if is_selected_wheel and self.edit_mode == "jump" else pos+1}/{wheel.size}"
                
                pin_str += Terminal.ResetStyle(gen = True)

                Terminal.Print(centerString(pin_str, (window.width - 1) // len(wheels), "-" if row == 2 else " "))
                Terminal.ResetStyle()
        
        # Text display
        Terminal.SetColor("yellow")
        # Ciphertext
        for i in range(5):
            Terminal.SetCursorPosition(22, 9 + i)
            Terminal.Print(" " * 20)
        for (i, line) in enumerate(wordWrap(self.machine.ciphertext, 20)[self.scroll : self.scroll + 5]):
            Terminal.SetCursorPosition(22, 9 + i)
            Terminal.Print(line)
        # Plaintext
        for i in range(5):
            Terminal.SetCursorPosition(1, 9 + i)
            Terminal.Print(" " * 20)
        for (i, line) in enumerate(wordWrap(self.machine.plaintext + ("_" if self.mode == "text" else ""), 20)[self.scroll : self.scroll + 5]):
            Terminal.SetCursorPosition(1, 9 + i)
            if line.endswith("_"):
                line = line[:-1] + Terminal.SetColor("white", gen=True) + "_"
            Terminal.Print(line)
        Terminal.ResetColor()
        
        Terminal.Flush()

main = Main()
window.Run(main)
print(main.machine.ciphertext)
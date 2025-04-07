from __future__ import annotations
from winter import *
from math import floor, ceil
from re import finditer
from textwrap import wrap as twrap

def wrap(sequence: str|list|tuple, length: int):
    return [sequence[i: i + length] for i in range(0, len(sequence), length)]

def wordWrap(text: str, width: int):
    paragraphs = text.split("\n")
    lines = []
    for p in paragraphs:
        lines += twrap(p, width)
    return lines

def ntol(n: int):
    return chr(65 + n % 26)

def lton(l: str):
    return (ord(l[:1].upper()) - 65) % 26

class Rotor:
    def __init__(self, wiring: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", notches: str = "", position: str = "A", next: Rotor = None, name: str = None):
        self.wiring:  list[int] = [lton(p) for p in wiring ] if type(wiring ) == str else wiring
        self.notches: list[int] = [lton(n) for n in notches] if type(notches) == str else notches
        self.position = lton(position)
        self.stepped = False
        self.doublestep = False
        self.next = next
        self.name = name
    def Step(self):
        if self.next:
            if self.next.doublestep and self.doublestep:
                self.next.Step()
                self.next.doublestep = False
            if self.position in self.notches:
                self.next.Step()
                self.doublestep = True
        self.position += 1
        self.position %= 26
    def Transform(self, letter: str):
        letter = lton(letter)
        return ntol(self.wiring[(letter - self.position) % 26] + self.position)
    def Inverse(self, letter: str):
        letter = lton(letter)
        return ntol(self.wiring.index((letter - self.position) % 26) + self.position)
    def Instantiate(self, position: str = "A", next: Rotor = None):
        return Rotor(self.wiring, self.notches, position, next, self.name)

rotors = {
    "1": Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "R",  name = "I"   ),
    "2": Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "F",  name = "II"  ),
    "3": Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "W",  name = "III" ),
	"4": Rotor("ESOVPZJAYQUIRHXLNFTGKDCMWB", "K",  name = "IV"  ),
	"5": Rotor("VZBRGITYUPSDNHLXAWMJQOFECK", "A",  name = "V"   ),
	"6": Rotor("JPGVOUMFYQBENHZRDKASXLICTW", "AN", name = "VI"  ),
	"7": Rotor("NZJHGRCXMYSWBOUFAIVLPEKQDT", "AN", name = "VII" ),
	"8": Rotor("FKQHTLXOCBJSPDZRAMEWNIUYGV", "AN", name = "VIII")
}

class Swapper:
    def __init__(self, pairs: list[str] = [], name: str = None):
        self.wiring: dict[str, str] = {}
        self.pairs: list[str] = []
        self.name = name
        for p in pairs:
            self.AddPair(p)
    def AddPair(self, pair: str):
        pair = pair.upper()
        if pair[0] in self.wiring or pair[1] in self.wiring:
            return
        self.pairs.append(pair)
        self.wiring[pair[0]], self.wiring[pair[1]] = pair[1], pair[0]
    def RemovePair(self, pair: str):
        pair = pair.upper()
        if not pair in self.pairs:
            return
        self.pairs.remove(pair)
        del self.wiring[pair[0]], self.wiring[pair[1]]
    def Transform(self, letter: str):
        letter = ntol(lton(letter))
        if letter in self.wiring:
            return self.wiring[letter]
        else:
            return letter
    def Instantiate(self):
        return Swapper(self.pairs, self.name)

reflectors = {
    "A": Swapper(['AE', 'BJ', 'CM', 'DZ', 'FL', 'GY', 'HX', 'IV', 'KW', 'NR', 'OQ', 'PU', 'ST'], name = "A"),
    "B": Swapper(['AY', 'BR', 'CU', 'DH', 'EQ', 'FS', 'GL', 'IP', 'JX', 'KN', 'MO', 'TZ', 'VW'], name = "B"),
    "C": Swapper(['AF', 'BV', 'CP', 'DJ', 'EI', 'GO', 'HY', 'KR', 'LZ', 'MX', 'NW', 'QT', 'SU'], name = "C")
}

class Enigma:
    def __init__(self, rotors: list[Rotor], reflector: Swapper, plugboard: Swapper):
        self.rotors = rotors
        for i in range(len(self.rotors) - 1):
            self.rotors[i].next = self.rotors[i + 1]
        self.reflector = reflector
        self.plugboard = plugboard
    def Transform(self, c: str):
        c = self.plugboard.Transform(c)
        for r in self.rotors:
            c = r.Transform(c)
        c = self.reflector.Transform(c)
        for r in reversed(self.rotors):
            c = r.Inverse(c)
        return self.plugboard.Transform(c)
    def Enter(self, c: str):
        if len(self.rotors) > 0:
            self.rotors[0].Step()
        return self.Transform(c)
    def Encode(self, txt: str):
        res = ""
        for c in txt:
            res += self.Enter(c)
        return res

# interface

window = Program(41, 13, "ENIGMA", killKey = "escape")

ALPHABET = [chr(i + 65) for i in range(26)]

class Main(ProgramState):
    def __init__(self):
        self.mode = "text"  # one of: 'text', 'rotor', 'plugboard', 'reflector'
        
        self.plaintext = ""
        self.ciphertext = ""
        self.scroll = 0
        
        self.rotor_cursor = 0
        
        self.plugboard_cursor = 0  # selected pair index
        self.plugboard_input = ""  # building a new pair
        
        self.cipher = Enigma([rotors["1"].Instantiate(), rotors["2"].Instantiate(), rotors["3"].Instantiate()], reflectors["A"].Instantiate(), Swapper())
        self.rotor_stack = []

    def Enter(self, prev):
        window.Clear()
        Terminal.ResetStyle()
        Terminal.SetCursorPosition(0, 1)
        Terminal.Print(
'''
║      rotors:            plugboard:      ║
║      XXXX: X<               __          ║
║      XXXX: X<       XX  XX  XX  XX  XX  ║
║      XXXX: X<       XX  XX  XX  XX  XX  ║
║                         XX  XX  XX      ║
║    reflector: X                         ║
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

# rotors: (7, 2 + i), 8
# reflector: (5, 6), 12
# plugboard:
#   input: (31, 2), 2
#   pairs: (23, 3 + i), 18
# text:
#   plaintext: (1, 9 + i), 20
#   ciphertext: (22, 9 + i), 20

    def Draw(self):
        Terminal.ResetStyle()
        Terminal.SetCursorPosition(1, 1)
        
        # rotors
        for i in range(3):
            Terminal.SetCursorPosition(7, 2 + i)
            sel = self.mode == "rotor" and self.rotor_cursor == i
            if sel:
                Terminal.EnableStyle("invert")
            Terminal.Print(centerString(f"{self.cipher.rotors[i].name}: {Terminal.EnableStyle("bold", gen = True)}{Terminal.SetColor("yellow", gen = True) if not sel else ""}{ntol(self.cipher.rotors[i].position)}{Terminal.ResetColor(gen = True)}{'<' if self.cipher.rotors[i].position in self.cipher.rotors[i].notches else ''}", 8))
            Terminal.ResetStyle()
        
        # reflector
        Terminal.SetCursorPosition(5, 6)
        if self.mode == "reflector":
            Terminal.EnableStyle("invert")
        Terminal.Print(centerString(f"reflector: {Terminal.EnableStyle("bold", gen = True)}{Terminal.SetColor("yellow", gen = True) if self.mode != "reflector" else ""}{self.cipher.reflector.name}", 12))
        Terminal.ResetStyle()

        # plugboard
        #   input
        Terminal.SetCursorPosition(30, 2)
        Terminal.EnableStyle("bold")
        if self.mode == "plugboard" and len(self.cipher.plugboard.pairs) == 0:
            Terminal.EnableStyle("invert")
        else:
            Terminal.SetColor("yellow")
        Terminal.Print(self.plugboard_input)
        Terminal.ResetColor()
        Terminal.Print("_" * (2 - len(self.plugboard_input)))
        Terminal.ResetStyle()
        #   pairs
        for i in range(3):
            Terminal.SetCursorPosition(22, 3 + i)
            Terminal.Print(" " * 18)
        for (i, line) in enumerate(wrap(self.cipher.plugboard.pairs, 5)):
            Terminal.SetCursorPosition(22, 3 + i)
            Terminal.EnableStyle("bold")
            Terminal.SetColor("yellow")
            for j in range(len(line)):
                if self.mode == "plugboard" and self.plugboard_cursor == 5 * i + j:
                    line[j] = Terminal.EnableStyle("invert", gen = True) + Terminal.ResetColor(gen = True) + line[j] + Terminal.DisableStyle("invert", gen = True) + Terminal.SetColor("yellow", gen = True)
            Terminal.Print(centerString(" ".join(line), 18))
            Terminal.ResetStyle()
        
        # text
        Terminal.SetColor("yellow")
        #   ciphertext
        for i in range(5):
            Terminal.SetCursorPosition(22, 9 + i)
            Terminal.Print(" " * 20)
        for (i, line) in enumerate(wordWrap(self.ciphertext, 20)[self.scroll : self.scroll + 5]):
            Terminal.SetCursorPosition(22, 9 + i)
            Terminal.Print(line)
        #   plaintext
        for i in range(5):
            Terminal.SetCursorPosition(1, 9 + i)
            Terminal.Print(" " * 20)
        for (i, line) in enumerate(wordWrap(self.plaintext + ("_" if self.mode == "text" else ""), 20)[self.scroll : self.scroll + 5]):
            Terminal.SetCursorPosition(1, 9 + i)
            if line[-1] == "_":
                line = line[:-1] + Terminal.SetColor("white", gen = True) + "_"
            Terminal.Print(line)
        Terminal.ResetColor()

        Terminal.Flush()

    def Keypress(self, key):
        if self.mode == "text":
            if key == "up":
                self.scroll -= 1
            elif key == "down":
                self.scroll += 1
            elif key == "backspace":
                if len(self.plaintext) > 0:
                    self.plaintext = self.plaintext[:-1]
                    self.ciphertext = self.ciphertext[:-1]
                    if len(self.rotor_stack) > 0:
                        for (i, p) in enumerate(self.rotor_stack.pop(-1)):
                            self.cipher.rotors[i].position = p
                self.scroll = -1
            elif key == "tab":
                self.mode = "rotor"
                self.rotor_cursor = 0
            elif key == "space":
                self.plaintext  += " "
                self.ciphertext += " "
                self.scroll = -1
            elif key == "enter":
                self.plaintext  += "\n"
                self.ciphertext += "\n"
                self.scroll = -1
            elif len(key) == 1:
                ch = key.upper()
                self.plaintext += ch
                if ch in ALPHABET:
                    self.rotor_stack.append(tuple(rotor.position for rotor in self.cipher.rotors))
                    self.ciphertext += self.cipher.Enter(ch)
                else:
                    self.ciphertext += ch
                self.scroll = -1

        elif self.mode == "rotor":
            p = self.rotor_cursor
            if key == "right":
                self.mode = "plugboard"
            elif key == "up":
                if p > 0:
                    p -= 1
            elif key == "down":
                if p < 2:
                    p += 1
                else:
                    self.mode = "reflector"
            elif key == "space":
                notches = [(n - self.cipher.rotors[p].position) % 26 for n in self.cipher.rotors[p].notches if n != self.cipher.rotors[p].position]
                self.cipher.rotors[p].position = (min(notches) + self.cipher.rotors[p].position) % 26
            elif key == "tab":
                self.mode = "text"
                self.scroll = -1
            else:
                ch = key.upper()
                if ch in rotors:
                    self.cipher.rotors[p] = rotors[ch].Instantiate()
                elif ch in ALPHABET:
                    self.cipher.rotors[p].position = lton(ch)
            self.rotor_cursor = p

        elif self.mode == "reflector":
            if key == "right":
                self.mode = "plugboard"
            elif key == "up":
                self.mode = "rotor"
                self.rotor_cursor = 2
            elif key == "tab":
                self.mode = "text"
                self.scroll = -1
            else:
                ch = key.upper()
                if ch in reflectors:
                    self.cipher.reflector = reflectors[ch].Instantiate()

        elif self.mode == "plugboard":
            p = self.plugboard_cursor
            pairs = self.cipher.plugboard.pairs
            pc = len(pairs)
            l, c = p // 5, p % 5
            lc = pc + (-pc % 5)
            ll = [min(pc - 5 * i, 5) for i in range(lc)]
            if key == "up":
                if l > 0:
                    p = p -   c - 5  + floor((1/2 - (ll[l] - 1) / 10 + c/4) * (ll[l - 1] - 1) + 0.5)
            elif key == "down":
                if l < lc - 1:
                    p = p + (-c % 5) + floor((1/2 - (ll[l] - 1) / 10 + c/4) * (ll[l + 1] - 1) + 0.5)
            elif key == "left":
                if c > 0:
                    p -= 1
                else:
                    self.mode = "rotor"
                    self.rotor_cursor = l
            elif key == "right":
                if p < pc - 1:
                    p += 1
            elif key == "backspace" or key == "delete":
                if p < pc:
                    self.cipher.plugboard.RemovePair(pairs[p])
                    p = max(0, p - 1)
                else:
                    self.plugboard_input = None
            elif key == "tab":
                self.mode = "text"
                self.scroll = -1
            else:
                ch = key.upper()
                if ch in ALPHABET and not ch in self.cipher.plugboard.wiring:
                    self.plugboard_input += ch
                    if len(self.plugboard_input) == 2:
                        self.cipher.plugboard.AddPair(self.plugboard_input)
                        p = pc
                        self.plugboard_input = ""
            self.plugboard_cursor = p

        lines = wordWrap(self.plaintext + ("_" if self.mode == "text" else ""), 20)
        self.scroll = max(0, min(len(lines) - 5, self.scroll) if self.scroll >= 0 else len(lines) - 5)

        self.Draw()

main = Main()

window.Run(main)

print(main.ciphertext)
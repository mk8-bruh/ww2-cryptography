from winter import *

program = Program(40, 15, "Hello World!", "escape")

class HelloWorld(ProgramState):
  def Enter(self, prev):
    program.Clear()
    Terminal.ResetStyle()
    Terminal.SetCursorPosition(1, 6)
    Terminal.Print(centerString("Hello world!!!", program.width))
    Terminal.Flush()
  def Keypress(self, key):
    Terminal.ResetStyle()
    Terminal.SetCursorPosition(1, 8)
    Terminal.Print(centerString(f"pressed key: {key}", program.width))
    Terminal.Flush()
  def Exit(self, next):
    Terminal.ResetStyle()
    Terminal.SetCursorPosition(1, 10)
    Terminal.Print(centerString(f"Goodbye!!!", program.width))
    Terminal.Flush()

program.Run(HelloWorld())
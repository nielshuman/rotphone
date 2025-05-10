from gpiozero import Button

class RotaryDial():
    def __init__(self, turnPin, pulsePin, onDigit=None):
        self._turnButton = Button(turnPin, bounce_time=0.01)
        self._pulseButton = Button(pulsePin, bounce_time=0.01)
        self._turnButton.when_pressed = self._onTurnStart
        self._turnButton.when_released = self._onTurnEnd
        self._count = 0
        self.onDigit = onDigit
        
    def _onTurnStart(self):
        # print("Turn start")
        self._count = 0
        self._pulseButton.when_pressed = self._onPulse
        
    def _onTurnEnd(self):
        # print("Turn end")
        self._pulseButton.when_pressed = None
        
        if self.onDigit is None:
            return
        
        if self._count >= 1 and self._count <= 9:
            self.onDigit(self._count)
        elif self._count == 10:
            self.onDigit(0)
        else:
            print(f"Invalid digit ({self._count} pulses)")
            
        
        
    def _onPulse(self):
        self._count += 1
        # print("Pulse")
        
    
    
rot = RotaryDial(20, 21)
rot.onDigit = lambda x: print(f"Digit: {x}")

while True:
    pass
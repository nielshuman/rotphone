from gpiozero import Button

class RotaryDial():
    def __init__(self, turnPin, pulsePin, onDigit=None, onError=None):
        self._turnButton = Button(turnPin, bounce_time=0.01)
        self._pulseButton = Button(pulsePin, bounce_time=0.01)
        self._turnButton.when_pressed = self._onTurnStart
        self._turnButton.when_released = self._onTurnEnd
        self._count = 0
        self.onDigit = onDigit
        self.onError = onError
        
    def _onTurnStart(self):
        self._count = 0
        self._pulseButton.when_pressed = self._onPulse
        
    def _onTurnEnd(self):
        self._pulseButton.when_pressed = None
        
        if self.onDigit is None:
            return
        
        if self._count >= 1 and self._count <= 9:
            self.onDigit(self._count)
        elif self._count == 10:
            self.onDigit(0)
        elif self.onError is not None:
            self.onError(f"Invalid digit ({self._count} pulses)")
            
    def _onPulse(self):
        self._count += 1

class Bells():
    def __init__(self):
        self.ringing = False
        pass
    
    def ring(self):
        if self.ringing:
            print("Already ringing")
            return
        
        self.ringing = True
        print("Ringing...")
        
    def stop(self):
        if not self.ringing:
            print("Not ringing")
            return
        
        self.ringing = False
        print("Stopped ringing")

rotaryDial = RotaryDial(20, 21)
phoneHook = Button(16, bounce_time=0.01)
bells = Bells()

def test():
    rotaryDial.onDigit = lambda digit: print(f"Digit: {digit}")
    rotaryDial.onError = lambda error: print(f"Error: {error}")
    phoneHook.when_pressed = lambda: print("Phone picked up")
    phoneHook.when_released = lambda: print("Phone hung up")
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    
if __name__ == "__main__":
    test()
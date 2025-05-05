from gpiozero import Button

t1 = Button(21, bounce_time=0.01)
t2 = Button(20, bounce_time=0.01)


t1.when_pressed = lambda: print('1 pressed!')
# t1.when_released = lambda: print('1 released!')
t2.when_pressed = lambda: print('==== 2 pressed! =====')
t2.when_released = lambda: print('==== 2 released! =====')


while True:
    
    
    
    pass
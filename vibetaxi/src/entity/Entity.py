import pygame

class Entity:
    def __init__(self, x, y, definition):
        self.x = x
        self.y = y
        
        self.width = definition.get("width", 32)
        self.height = definition.get("height", 32)
        
        self.def_data = definition
        
        self.vx = 0
        self.vy = 0
        
        self.state_machine = None

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        if self.state_machine:
            self.state_machine.update(dt)

    def render(self, surface):
        if self.state_machine:
            self.state_machine.render(surface)

    def on_input(self, input_id, input_data):
        if self.state_machine:
            self.state_machine.on_input(input_id, input_data)
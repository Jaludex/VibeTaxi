from gale.command import Command

class AccelerateCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_accelerating = True

class StopAccelerateCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_accelerating = False

class BrakeCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_braking = True

class StopBrakeCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_braking = False

class ReverseCommand:
    def execute(self, entity):
        entity.is_reversing = True

class StopReverseCommand:
    def execute(self, entity):
        entity.is_reversing = False

ACCELERATE = AccelerateCommand()
STOP_ACCELERATE = StopAccelerateCommand()
BRAKE = BrakeCommand()
STOP_BRAKE = StopBrakeCommand()
REVERSE = ReverseCommand()
STOP_REVERSE = StopReverseCommand()
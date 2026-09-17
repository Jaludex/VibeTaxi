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

class ReverseCommand(Command):
    def execute(self, entity, dt: float = 0.0) -> None:
        entity.is_reversing = True

class StopReverseCommand(Command):
    def execute(self, entity, dt: float = 0.0) -> None:
        entity.is_reversing = False

class DriftCommand(Command):
    def execute(self, entity, dt: float = 0.0) -> None:
        entity.is_drifting = True

class StopDriftCommand(Command):
    def execute(self, entity, dt: float = 0.0) -> None:
        entity.is_drifting = False

class RadioVolumeUpCommand(Command):
    def execute(self, radio, dt: float = 0.0) -> None:
        radio.volume_up()

class RadioVolumeDownCommand(Command):
    def execute(self, radio, dt: float = 0.0) -> None:
        radio.volume_down()

class RadioNextStationCommand(Command):
    def execute(self, radio, dt: float = 0.0) -> None:
        radio.next_station()

class RadioPrevStationCommand(Command):
    def execute(self, radio, dt: float = 0.0) -> None:
        radio.prev_station()

ACCELERATE = AccelerateCommand()
STOP_ACCELERATE = StopAccelerateCommand()
BRAKE = BrakeCommand()
STOP_BRAKE = StopBrakeCommand()
REVERSE = ReverseCommand()
STOP_REVERSE = StopReverseCommand()
DRIFT = DriftCommand()
STOP_DRIFT = StopDriftCommand()

RADIO_VOL_UP = RadioVolumeUpCommand()
RADIO_VOL_DOWN = RadioVolumeDownCommand()
RADIO_NEXT_STATION = RadioNextStationCommand()
RADIO_PREV_STATION = RadioPrevStationCommand()
from typing import TypeVar
from gale.state import BaseState
from gale.state import StateMachine

class BaseEntityState(BaseState):
    def __init__(
        self, entity: TypeVar("Entity"), state_machine: StateMachine
    ) -> None:
        super().__init__(state_machine)
        self.entity = entity
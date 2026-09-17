# CollidableMixin has been removed — physics now drives collisions via gale.physics.
# This file remains for compatibility but should not be imported.

class CollidableMixin:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("CollidableMixin is deprecated. Use gale.physics bodies instead.")

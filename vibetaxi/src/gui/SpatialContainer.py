from gale.ui.container import Container
from gale.ui.widget import Direction


class SpatialContainer(Container):
    def _move_focus(self, direction: Direction) -> bool:
        focusable = self._focusable_children()

        if not focusable:
            return False

        dx, dy = direction
        current = self._focused_child()

        if current is None:
            self._focus_only(focusable[0])
            return True

        best_child = None
        best_score = float("inf")

        cx1 = current.x + getattr(current, "width", 0) / 2
        cy1 = current.y + getattr(current, "height", 0) / 2

        for child in focusable:
            if child is current:
                continue

            cx2 = child.x + getattr(child, "width", 0) / 2
            cy2 = child.y + getattr(child, "height", 0) / 2

            vx = cx2 - cx1
            vy = cy2 - cy1

            dot = vx * dx + vy * dy

            if dot > 0:
                dist = (vx**2 + vy**2) ** 0.5
                cross = abs(vx * dy - vy * dx)

                score = dist + cross * 2

                if score < best_score:
                    best_score = score
                    best_child = child

        if best_child is not None:
            self._focus_only(best_child)
            return True

        return False


from gale.ui.window import Window


class SpatialWindow(SpatialContainer, Window):
    pass


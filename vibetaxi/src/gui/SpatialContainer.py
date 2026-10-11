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

        x1 = current.x
        y1 = current.y
        w1 = getattr(current, "width", 0)
        h1 = getattr(current, "height", 0)
        r1 = x1 + w1
        b1 = y1 + h1

        cx1 = x1 + w1 / 2.0
        cy1 = y1 + h1 / 2.0

        for child in focusable:
            if child is current:
                continue

            x2 = child.x
            y2 = child.y
            w2 = getattr(child, "width", 0)
            h2 = getattr(child, "height", 0)
            r2 = x2 + w2
            b2 = y2 + h2

            cx2 = x2 + w2 / 2.0
            cy2 = y2 + h2 / 2.0

            vx = cx2 - cx1
            vy = cy2 - cy1

            # Candidate must be in the general half-plane of the input direction
            dot = vx * dx + vy * dy
            if dot <= 0:
                continue

            # Strict directional checks along cardinal directions to reject elements
            # that are strictly in the opposite half
            if dy > 0 and (cy2 <= cy1 or b2 <= y1 + 1):
                continue
            if dy < 0 and (cy2 >= cy1 or y2 >= b1 - 1):
                continue
            if dx > 0 and (cx2 <= cx1 or r2 <= x1 + 1):
                continue
            if dx < 0 and (cx2 >= cx1 or x2 >= r1 - 1):
                continue

            # Projections & Overlaps
            overlap_x = max(0.0, min(r1, r2) - max(x1, x2))
            overlap_y = max(0.0, min(b1, b2) - max(y1, y2))

            # Edge-to-edge gaps
            gap_x = 0.0 if overlap_x > 0 else (x2 - r1 if x2 > r1 else x1 - r2)
            gap_y = 0.0 if overlap_y > 0 else (y2 - b1 if y2 > b1 else y1 - b2)

            if abs(dx) > abs(dy):
                # Horizontal movement:
                # If candidate overlaps horizontally with current, but is separated vertically,
                # it is strictly above or below current - reject it for horizontal navigation.
                if overlap_x > 0 and overlap_y <= 0:
                    continue

                # Prioritize elements in the same row
                row_penalty = 1000.0 if overlap_y <= 0 else 0.0
                score = row_penalty + gap_x + gap_y * 4.0 + abs(vy) * 0.5
            elif abs(dy) > abs(dx):
                # Vertical movement:
                # If candidate overlaps vertically with current, but is separated horizontally,
                # it is strictly to the left or right of current - reject it for vertical navigation.
                if overlap_y > 0 and overlap_x <= 0:
                    continue

                # In vertical movement, moving to the next row (gap_y) is primary,
                # with horizontal offset (gap_x) and alignment (abs(vx)) as secondary factors.
                score = gap_y * 2.0 + gap_x * 0.5 + abs(vx) * 0.2
            else:
                # Diagonal movement
                score = (gap_x**2 + gap_y**2)**0.5 + (vx**2 + vy**2)**0.5 * 0.1

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


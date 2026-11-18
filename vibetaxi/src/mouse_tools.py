import pygame
import settings


def get_real_window_size() -> tuple[float, float]:
    """Return the physical window or screen dimensions in pixels."""
    from src.os_tools import is_android
    if is_android():
        if hasattr(pygame.display, "get_desktop_sizes"):
            try:
                sizes = pygame.display.get_desktop_sizes()
                if sizes and len(sizes) > 0:
                    sw, sh = sizes[0]
                    if sw > 0 and sh > 0:
                        return float(max(sw, sh)), float(min(sw, sh))
            except Exception:
                pass
        try:
            info = pygame.display.Info()
            if getattr(info, "current_w", 0) > 0 and getattr(info, "current_h", 0) > 0:
                return float(max(info.current_w, info.current_h)), float(min(info.current_w, info.current_h))
        except Exception:
            pass

    if hasattr(pygame.display, "get_window_size"):
        try:
            w, h = pygame.display.get_window_size()
            if w > 0 and h > 0:
                return float(w), float(h)
        except Exception:
            pass

    surface = pygame.display.get_surface()
    if surface:
        w, h = surface.get_size()
        if w > 0 and h > 0:
            return float(w), float(h)

    return float(settings.WINDOW_WIDTH), float(settings.WINDOW_HEIGHT)


def get_letterbox_info() -> tuple[float, float, float, float]:
    """Returns (render_w, render_h, offset_x, offset_y) for the current display.
    
    If the current surface is already in virtual resolution (e.g. SCALED mode),
    returns (VIRTUAL_WIDTH, VIRTUAL_HEIGHT, 0.0, 0.0).
    """
    surface = pygame.display.get_surface()
    if surface:
        surf_w, surf_h = surface.get_size()
        if surf_w == settings.VIRTUAL_WIDTH and surf_h == settings.VIRTUAL_HEIGHT:
            return float(surf_w), float(surf_h), 0.0, 0.0

    win_w, win_h = get_real_window_size()
    virt_w = float(settings.VIRTUAL_WIDTH)
    virt_h = float(settings.VIRTUAL_HEIGHT)

    win_aspect = win_w / win_h
    virt_aspect = virt_w / virt_h

    if abs(win_aspect - virt_aspect) < 0.01:
        return float(win_w), float(win_h), 0.0, 0.0

    if win_aspect > virt_aspect:
        # Screen is wider than virtual aspect (e.g. 20:9 phone vs 16:9 game)
        # Black bars on left and right
        render_h = float(win_h)
        render_w = render_h * virt_aspect
        offset_x = (win_w - render_w) / 2.0
        offset_y = 0.0
    else:
        # Screen is taller than virtual aspect
        # Black bars on top and bottom
        render_w = float(win_w)
        render_h = render_w / virt_aspect
        offset_x = 0.0
        offset_y = (win_h - render_h) / 2.0

    return render_w, render_h, offset_x, offset_y


def physical_to_virtual(physical_x: float, physical_y: float) -> tuple[float, float]:
    """Convert screen/mouse physical pixel coordinates to virtual coordinates."""
    surface = pygame.display.get_surface()
    if surface:
        surf_w, surf_h = surface.get_size()
        # In SCALED mode, SDL2 already converted mouse event.pos to virtual coordinates!
        if surf_w == settings.VIRTUAL_WIDTH and surf_h == settings.VIRTUAL_HEIGHT:
            return float(physical_x), float(physical_y)

    render_w, render_h, offset_x, offset_y = get_letterbox_info()
    virtual_x = (physical_x - offset_x) / render_w * settings.VIRTUAL_WIDTH
    virtual_y = (physical_y - offset_y) / render_h * settings.VIRTUAL_HEIGHT
    return virtual_x, virtual_y


def virtual_to_physical(virtual_x: float, virtual_y: float) -> tuple[float, float]:
    """Convert virtual coordinates to physical screen pixels."""
    surface = pygame.display.get_surface()
    if surface:
        surf_w, surf_h = surface.get_size()
        if surf_w == settings.VIRTUAL_WIDTH and surf_h == settings.VIRTUAL_HEIGHT:
            return float(virtual_x), float(virtual_y)

    render_w, render_h, offset_x, offset_y = get_letterbox_info()
    physical_x = (virtual_x / settings.VIRTUAL_WIDTH) * render_w + offset_x
    physical_y = (virtual_y / settings.VIRTUAL_HEIGHT) * render_h + offset_y
    return physical_x, physical_y


def finger_to_virtual(event_x: float, event_y: float) -> tuple[float, float]:
    """Convert SDL2 normalized touch coordinates (0.0 to 1.0) to virtual coordinates.
    
    SDL2 on Android with pygame.SCALED already maps touch coordinates to the
    logical game display viewport (0.0 to 1.0).
    """
    virt_w = float(settings.VIRTUAL_WIDTH)
    virt_h = float(settings.VIRTUAL_HEIGHT)
    vx = event_x * virt_w
    vy = event_y * virt_h
    return max(0.0, min(virt_w, vx)), max(0.0, min(virt_h, vy))

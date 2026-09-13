import settings

def physical_to_virtual(physical_x: float, physical_y: float) -> tuple[float, float]:
    scale_x = settings.WINDOW_WIDTH / settings.VIRTUAL_WIDTH
    scale_y = settings.WINDOW_HEIGHT / settings.VIRTUAL_HEIGHT
    
    virtual_x = physical_x / scale_x
    virtual_y = physical_y / scale_y
    
    return virtual_x, virtual_y

def virtual_to_physical(virtual_x: float, virtual_y: float) -> tuple[float, float]:
    scale_x = settings.WINDOW_WIDTH / settings.VIRTUAL_WIDTH
    scale_y = settings.WINDOW_HEIGHT / settings.VIRTUAL_HEIGHT
    
    physical_x = virtual_x * scale_x
    physical_y = virtual_y * scale_y
    
    return physical_x, physical_y
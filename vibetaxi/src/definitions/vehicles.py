# src/definitions/vehicles.py

VEHICLE_DEFS = {
    "yellow_taxi": {
        "texture": "cars",
        "frame": 0,
        "max_speed": 300,
        "acceleration": 200, 
        "friction": 300,      
        "turn_speed": 4.0,    
        "base_health": 100,
    },
    
    "blue_sedan": {
        "width": 60,
        "height": 30,
        "texture": "sedan-blue",
        "max_speed": 200,
        "acceleration": 150,
        "friction": 250,
        "turn_speed": 3.0,
        "base_health": 80,
    },
    
    "city_bus": {
        "width": 120,
        "height": 40,
        "texture": "city-bus",
        "max_speed": 120,
        "acceleration": 50,    
        "friction": 100,       
        "turn_speed": 1.5,    
        "base_health": 300,
    },
    

    "red_moto": {
        "width": 30,
        "height": 15,
        "texture": "moto-red",
        "max_speed": 450,
        "acceleration": 600,  
        "friction": 400,
        "turn_speed": 7.0,
        "base_health": 30,
    }
}
import settings

texts = {
    "en": {
        "language_name": "English",

        # --- UI & Menus ---
        "game_title": "Vibe Taxi",
        "version": "Version {version}",
        "fullscreen_hint": "F11 for Fullscreen",
        
        # Buttons
        "btn_new_game": "New Game",
        "btn_resume_work_day": "Resume Work. Day: {day}",
        "btn_resume_work": "Resume Work",
        "btn_records": "Records",
        "btn_credits": "Credits",
        "btn_quit_game": "Quit Game",
        "btn_user_tracks": "User Tracks",
        "btn_language": "Language",
        "btn_tutorial": "Tutorial",
        "btn_workday": "Workday",
        "btn_arcade": "Arcade",
        "btn_zen": "Zen",
        "btn_yes": "Yes",
        "btn_no": "No",
        "btn_ok": "OK",
        "btn_next": "Next",
        "btn_resume": "Continue",
        "btn_exit_menu": "Main Menu",
        "btn_quit_desktop": "Quit Game",
        "btn_repair_taxi": "Repair Taxi",
        "btn_repair_taxi_cost": "Repair - ${cost}",
        "btn_save_quit": "Save & Exit",
        "btn_continue": "Continue",
        "btn_submit": "Save",
        "btn_back": "Back",
        
        # Messages & Texts
        "msg_user_tracks_title": "User Tracks",
        "msg_user_tracks_info": "You can add your own music \ntracks to the game!\nAfter this message, a folder will\nopen where you can place your files.\nThe game supports .mp3, .ogg and .wav files.\nAfter adding songs, restart the game\nto load them\nBy adding music to this folder, you confirm\nyou have the rights or licenses to use it\nThe developers assume no liability for copyrighted content.",
        "msg_credits_title": "Credits",
        "msg_credits_text": "VIBE TAXI\nA game made with Gale & Pygame.\nAs Project in the course of\nVideogame Programming I (ULA)\nDevelopment & Design:\nJesus Leon (Jaludex)\nZadkiel Jimenez (Eltoti)\n\nMusic & Sound Effects:\nopengameart.org\npixabay.com\nText blips by dmochas on itch.io\nGraphical Assets:\nRadio, indicator arrow and passenger UI by Eltoti\nCity Assets by nyknck on itch.io\nPeds texture by vimlark on itch.io\nFonts:\nGoogle Fonts\n\nThanks for playing our game!\nHope you enjoy it and have a good time!\n",
        "msg_lang_title": "Select Language",
        
        "mode_selection_title": "Select Mode",
        "mode_tutorial_desc": "Learn the basics of the game",
        "mode_workday_desc": "Win money with each trip. Use it to repare your car",
        "mode_arcade_desc": "Win as many trips as you can before time runs out",
        "mode_zen_desc": "No damage, no limits. Just chill and drive.",

        "mode_workday_initial_text": "Day {self.day}\nToday's fee: ${self.fee:.2f}",
        "mode_arcade_initial_text": "Go get them!",
        "mode_zen_initial_text": "Relax and enjoy the ride.",
        
        "records_title": "Hall of Fame",
        "records_workday_format": "{i}. {name} - Day {score}",
        "records_arcade_format": "{i}. {name} - {score} pts",
        
        "pause_title": "Paused",
        "game_over_title": "Game Over",
        "game_over_money": "Money Made: ${score:.2f}",
        "game_over_pax": "Passengers: {score}",
        "end_of_day_title_format": "End of Day {day}",
        "end_of_day_money": "Money Left: ${money:.2f}",
        
        "new_record_title": "New Record!",
        "new_record_score": "Score: {score}",
        
        "confirm_overwrite": "Overwrite existing save?",
        
        # Gameplay
        "hud_score_label": "SCORE",
        "hud_score_value": "{score}",
        "hud_money_label": "MONEY",
        "hud_money_value": "${money:.2f}",
        "bonus_fast": "Fast!",
        "bonus_safe": "Safe!",
        "hud_tutorial": "TUTORIAL",
        "hud_zen": "ZEN",
        
        # Confirmation
        "confirm_quit": "Are you sure you want to quit?",
        
        # Tutorial
        "tutorial_title": "Tutorial",
        "tutorial_completed_title": "Tutorial Completed!",
        "tutorial_completed_msg": "You have completed the tutorial. Ready for the real work!",
        "tutorial_msg_welcome": "Welcome to VibeTaxi, in this game you will become the best taxi driver by finding the music your passengers love. Use the mouse click to drive",
        "tutorial_msg_controls": "Try moving around this area. Move the mouse cursor to turn, use \"x\" to  brake and \"z\" to go in reverse. Pause with ESC",
        "tutorial_msg_pickup": "Now try picking up that client. Get close to him and brake, then take him to his destination",
        "tutorial_msg_radio": "Now lets try with this another client, listen to him. Use WASD to change the radio station and volume, try playing something he/she likes",
        "tutorial_msg_obstacles": "Now try getting to the end of this section, try avoiding the cones and traffic and get the client to his destination. Good Luck!",
        "tutorial_msg_vibe": "Great, you're in Vibe Mode, now you can drift to keep your speed. Drift with SHIFT",
        
        # --- Passenger Dialogues ---
        "dialogues": {
            "enter": [
                "Hi! Take me to {destination}, please.",
                "Hey boss. Let's go to {destination}, I'm in a hurry.",
                "Hello there. I need to get to {destination}.",
                "Good day. Drop me off at {destination}.",
                "Yo. To {destination}, step on it!"
            ],
            "hints": {
                "rock": [
                    "I need some loud guitars to wake me up.",
                    "Put on something heavy, man.",
                    "Got any classic rock?",
                    "I feel like headbanging right now.",
                    "I need some distortion and a good guitar solo.",
                    "Let's hear some riffs, driver.",
                    "I want to listen to a real band, not a computer."
                ],
                "pop": [
                    "I want to listen to something catchy.",
                    "Put on the top hits, please.",
                    "I need some upbeat vocals to sing along to.",
                    "Got any mainstream pop?",
                    "I'm in the mood for something fun and popular.",
                    "Play something everyone knows the lyrics to.",
                    "I love chart-topping tracks."
                ],
                "jazz": [
                    "I need something smooth and relaxing.",
                    "Got any saxophones on the radio?",
                    "I'd love some nice background piano or jazz.",
                    "Put on some jazz if you have it.",
                    "I want to vibe to some old rhythms.",
                    "Let's listen to some jazzy tunes.",
                    "Nothing beats a good brass section."
                ],
                "hiphop": [
                    "Put on some beats, driver.",
                    "I need some sick rhymes to get hyped.",
                    "Got any rap stations?",
                    "Let's listen to some hip-hop.",
                    "Turn up the bass and put on some MCs.",
                    "I want to hear some good flow.",
                    "Play some urban tracks."
                ],
                "electronic": [
                    "I want to hear some heavy synths.",
                    "Put on some EDM or techno, please.",
                    "I need a fast BPM to get going.",
                    "Got any club music?",
                    "I want to feel like I'm in a club.",
                    "Man i love Synths",
                    "I need some electronic dance tracks."
                ],
            },
            "reaction": {
                "good": [
                    "This song is amazing!", 
                    "What a track! Turn it up.", 
                    "You have great taste in music.",
                    "This is exactly what I wanted to hear.",
                    "Awesome vibes, driver!"
                ],
                "neutral": [
                    "...", 
                    "You can leave this on, it's fine.",
                    "This song is okay.",
                    "Not my favorite, but not bad.",
                    "I don't mind this track."
                ],
                "bad": [
                    "Hey! Be more careful!", 
                    "My head hurts.", 
                    "You're not carrying potatos, are you?",
                    "I can't stand this shaking",
                    "Wait a minute, are you drunk?"
                ]
            },
            "exit": {
                "good": [
                    "Excellent service, 5 stars!", 
                    "Thank you, that was a very pleasant ride.", 
                    "See ya! Thanks for the good vibes!",
                    "Perfect driving, keep it up.",
                    "I'll definitely recommend this taxi."
                ],
                "bad": [
                    "Terrible ride. I'm disgusted.", 
                    "I am never getting in this taxi again.", 
                    "Finally we arrived, what a torture...",
                    "Worst cab experience of my life.",
                    "You're not getting a tip for this."
                ]
            }
        }
    },
    "es": {
        "language_name": "Español",

        # --- UI & Menus ---
        "game_title": "Vibe Taxi",
        "version": "Versión {version}",
        "fullscreen_hint": "F11 para Pantalla Completa",
        
        # Buttons
        "btn_new_game": "Nueva Partida",
        "btn_resume_work_day": "Reanudar Jornada. Día: {day}",
        "btn_resume_work": "Reanudar Jornada",
        "btn_records": "Puntuaciones",
        "btn_credits": "Créditos",
        "btn_quit_game": "Salir del Juego",
        "btn_user_tracks": "Música Propia",
        "btn_language": "Idioma",
        "btn_tutorial": "Tutorial",
        "btn_workday": "Jornada",
        "btn_arcade": "Arcade",
        "btn_zen": "Zen",
        "btn_yes": "Sí",
        "btn_no": "No",
        "btn_ok": "Aceptar",
        "btn_next": "Siguiente",
        "btn_resume": "Continuar",
        "btn_exit_menu": "Menú Principal",
        "btn_quit_desktop": "Salir al Escritorio",
        "btn_repair_taxi": "Reparar Taxi",
        "btn_repair_taxi_cost": "Reparar - ${cost}",
        "btn_save_quit": "Guardar y Salir",
        "btn_continue": "Continuar",
        "btn_submit": "Guardar",
        "btn_back": "Volver",
        
        # Messages & Texts
        "msg_user_tracks_title": "Música Propia",
        "msg_user_tracks_info": "¡Puedes añadir tu propia música \nal juego!\nDespués de este mensaje, se abrirá una\ncarpeta donde puedes poner tus archivos.\nEl juego soporta archivos .mp3, .ogg y .wav.\nDespués de añadir canciones, reinicia el juego\npara cargarlas.\nAl añadir música a esta carpeta, confirmas\nque tienes los derechos o licencias para usarla.\nLos desarrolladores no asumen responsabilidad por contenido con derechos de autor.",
        "msg_credits_title": "Créditos",
        "msg_credits_text": "VIBE TAXI\nUn juego hecho con Gale y Pygame.\nComo Proyecto en el curso de\nProgramación de Videojuegos I (ULA)\nDesarrollo y Diseño:\nJesús León (Jaludex)\nZadkiel Jiménez (Eltoti)\n\nMúsica y Efectos de Sonido:\nopengameart.org\npixabay.com\nPitidos de texto por dmochas en itch.io\nRecursos Gráficos:\nInterfaz de radio, flecha indicadora y pasajeros por Eltoti\nRecursos de Ciudad por nyknck en itch.io\nTextura de peatones por vimlark en itch.io\nFuentes:\nGoogle Fonts\n\n¡Gracias por jugar nuestro juego!\n¡Esperamos que lo disfrutes y pases un buen rato!\n",
        "msg_lang_title": "Seleccionar Idioma",
        
        "mode_selection_title": "Seleccionar Modo",
        "mode_tutorial_desc": "Aprende los conceptos básicos del juego",
        "mode_workday_desc": "Gana dinero con cada viaje. Úsalo para reparar tu auto.",
        "mode_arcade_desc": "Completa la mayor cantidad de viajes antes de que se acabe el tiempo.",
        "mode_zen_desc": "Sin daños, sin límites. Solo relájate y conduce.",

        "mode_workday_initial_text": "Día {day}\nPago de hoy: ${fee:.2f}",
        "mode_arcade_initial_text": "Empieza a recoger clientes!",
        "mode_zen_initial_text": "Relajate y disfruta el viaje.",
        
        "records_title": "Salón de la Fama",
        "records_workday_format": "{i}. {name} - Día {score}",
        "records_arcade_format": "{i}. {name} - {score} pts",
        
        "pause_title": "Pausa",
        "game_over_title": "Fin del Juego",
        "game_over_money": "Dinero Ganado: ${score:.2f}",
        "game_over_pax": "Pasajeros: {score}",
        "end_of_day_title_format": "Fin del Día {day}",
        "end_of_day_money": "Dinero Restante: ${money:.2f}",
        
        "new_record_title": "¡Nuevo Récord!",
        "new_record_score": "Puntuación: {score}",
        
        "confirm_overwrite": "¿Sobrescribir partida existente?",
        
        # Gameplay
        "hud_score_label": "PUNTOS",
        "hud_score_value": "{score}",
        "hud_money_label": "DINERO",
        "hud_money_value": "${money:.2f}",
        "bonus_fast": "¡Rápido!",
        "bonus_safe": "¡Seguro!",
        "hud_tutorial": "TUTORIAL",
        "hud_zen": "ZEN",
        
        # Confirmation
        "confirm_quit": "¿Estás seguro de que quieres salir?",
        
        # Tutorial
        "tutorial_title": "Tutorial",
        "tutorial_completed_title": "¡Tutorial Completado!",
        "tutorial_completed_msg": "¡Has completado el tutorial! Listo para el trabajo real.",
        "tutorial_msg_welcome": "Bienvenido a VibeTaxi, en este juego te convertirás en el mejor taxista encontrando la música que les encanta a tus pasajeros. Usa el clic del ratón para conducir.",
        "tutorial_msg_controls": "Intenta moverte por esta zona. Mueve el cursor del ratón para girar, usa \"x\" para frenar y \"z\" para ir en reversa. Pausa con ESC.",
        "tutorial_msg_pickup": "Ahora intenta recoger a ese cliente. Acércate a él y frena, luego llévalo a su destino.",
        "tutorial_msg_radio": "Ahora probemos con este otro cliente, escúchalo. Usa WASD para cambiar la estación de radio y el volumen, intenta poner algo que le guste.",
        "tutorial_msg_obstacles": "Ahora intenta llegar al final de esta sección, esquivando los conos y el tráfico y llevando al cliente a su destino. ¡Buena suerte!",
        "tutorial_msg_vibe": "Genial, estás en Modo Vibe, ahora puedes derrapar para mantener tu velocidad. Derrapa con SHIFT.",
        
        # --- Passenger Dialogues ---
        "dialogues": {
            "enter": [
                "¡Hola! Llévame a {destination}, por favor.",
                "Qué tal jefe. Vamos a {destination}, tengo prisa.",
                "Hola. Necesito llegar a {destination}.",
                "Buen día. Déjeme en {destination}.",
                "Oye. A {destination}, ¡acelera!"
            ],
            "hints": {
                "rock": [
                    "Necesito unas guitarras ruidosas para despertar.",
                    "Pon algo pesado, amigo.",
                    "¿Tienes algo de rock clásico?",
                    "Me apetece mover la cabeza con el ritmo un rato.",
                    "Necesito algo de distorsión y un buen solo de guitarra.",
                    "A ver esos riffs, conductor.",
                    "Quiero escuchar una banda real, no una computadora."
                ],
                "pop": [
                    "Quiero escuchar algo pegadizo.",
                    "Pon los éxitos del momento, por favor.",
                    "Necesito una voz alegre para cantar a la par.",
                    "¿Tienes algo de pop comercial?",
                    "Estoy de humor para algo divertido y popular.",
                    "Pon algo de lo que todos se sepan la letra.",
                    "Me encantan las canciones que son número uno."
                ],
                "jazz": [
                    "Necesito algo suave y relajante.",
                    "¿Hay algún saxofón en la radio?",
                    "Me encantaría un buen piano de fondo o jazz.",
                    "Pon algo de jazz si tienes.",
                    "Quiero disfrutar de unos ritmos antiguos.",
                    "Escuchemos algunas melodías de jazz.",
                    "No hay nada como una buena sección de vientos."
                ],
                "hiphop": [
                    "Pon unos buenos beats, conductor.",
                    "Necesito unas buenas rimas para animarme.",
                    "¿Tienes alguna emisora de rap?",
                    "Escuchemos algo de hip-hop.",
                    "Sube los bajos y pon a algunos MCs.",
                    "Quiero escuchar un buen flow.",
                    "Pon algunas pistas urbanas."
                ],
                "electronic": [
                    "Quiero escuchar unos buenos sintetizadores.",
                    "Pon algo de EDM o techno, por favor.",
                    "Necesito un BPM rápido para activarme.",
                    "¿Tienes música de club?",
                    "Quiero sentir que estoy en una discoteca.",
                    "Amigo, me encantan los sintetizadores.",
                    "Necesito unas buenas pistas de electrónica para bailar."
                ],
            },
            "reaction": {
                "good": [
                    "¡Esta canción es increíble!", 
                    "¡Qué temazo! Súbele al volumen.", 
                    "Tienes un gusto musical excelente.",
                    "Esto es exactamente lo que quería escuchar.",
                    "¡Excelentes vibras, conductor!"
                ],
                "neutral": [
                    "...", 
                    "Puedes dejar esto, está bien.",
                    "Esta canción está pasable.",
                    "No es mi favorita, pero no está mal.",
                    "No me molesta esta canción."
                ],
                "bad": [
                    "Ey! Ten mas cuidado!", 
                    "Me duele la cabeza.", 
                    "No estas llevando papas ¿Verdad?",
                    "No aguanto este ajetreo",
                    "Espera un momento, ¿Estás borracho?"
                ]
            },
            "exit": {
                "good": [
                    "¡Excelente servicio, 5 estrellas!", 
                    "Gracias, fue un viaje muy agradable.", 
                    "¡Nos vemos! ¡Gracias por la buena vibra!",
                    "Conducción perfecta, sigue así.",
                    "Definitivamente recomendaré este taxi."
                ],
                "bad": [
                    "Viaje terrible. Estoy indignado.", 
                    "No me vuelvo a subir a este taxi.", 
                    "Al fin llegamos, qué tortura...",
                    "La peor experiencia en taxi de mi vida.",
                    "No te daré propina por esto."
                ]
            }
        }
    }
    
}

def tr(key: str, default: str = None, **kwargs):
    """
    Helper function to get text comfortably.
    Usage: tr("btn_resume_work_day", day=3)
    """
    lang = getattr(settings, 'LANGUAGE', 'en')
    if not lang:
        lang = 'en'
        
    lang_dict = texts.get(lang, texts.get('en', {}))
    
    fallback = texts.get('en', {}).get(key, default if default is not None else key)
    text = lang_dict.get(key, fallback)
    
    if isinstance(text, str) and kwargs:
        return text.format(**kwargs)
    return text

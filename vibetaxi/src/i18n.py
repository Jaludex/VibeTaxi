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
        
        "records_title": "Hall of Fame",
        "records_workday_format": "{i}. {name} - Day {score}",
        "records_arcade_format": "{i}. {name} - {score} fares",
        
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
        "hud_score": "Score: {score}",
        "hud_money": "Money: ${money:.2f}",
        "hud_tutorial": "TUTORIAL",
        "hud_zen": "ZEN",
        
        # Confirmation
        "confirm_quit": "Are you sure you want to quit?",
        
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
                    "Could you change that music, please?", 
                    "What is this noise? My head hurts.", 
                    "Turn that garbage off right now.",
                    "I can't stand this genre.",
                    "This is awful, change the station!"
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

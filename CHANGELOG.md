Notable changes on the project will be documented here

# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), version format by [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.3.0 - 2026-09-26

### Added
 - Full localization and internationalization system (i18n) supporting English and Spanish across menus, HUD, dialogues, records, and tutorial maps
 - Performance ranking system (F, E, D, C, B, A, VIBE) for Game Over screen with custom colors, thresholds, reveal animations, and dedicated rank reveal sound effects
 - Arcade mode scoring overhaul based on fares, fast arrival bonuses, and safe driving bonuses
 - Animated roll-up tween for score and money counters in Arcade and Workday modes
 - Dynamic floating bonus popups next to HUD counters upon delivering passengers
 - New bonus sound effect played when achieving fast or safe arrival bonuses
 - Passenger rear-view portrait shake effect when crashing the taxi
 - Destination arrow animation tweening from the taxi towards the screen edge when a passenger boards
 - Passenger comfort drain mechanism when listening to disliked music stations for too long

### Changed
 - Redesigned HUD to display large numeric score/money values with centered descriptive labels below the taximeter
 - Game Over panel resized and redesigned to display performance ranks with delayed opacity tweening
 - Centralized game balance parameters, scoring constants, and ranking thresholds in `settings.py`

### Fixed
 - Fix repair cost in EndOfDayState not updating the money label after vehicle repairs
 - Fix passenger wobble animation duration reset on collision
 - Fix passenger ride time double-incrementing per frame
 - Fix tutorial tilemap strings by converting them to translation keys
 - Fix string formatting KeyError in Workday initial day text

## 1.2.0 - 2026-09-19

## Added
 - Finished south part of the city

## Changed
 - Game Logo

## Fixed
 - Fix duplicated tile objects ID from work in parallel with the same map
 - Fix Soutch city spawn having a passenger spawning right by it's side
 - Fix Passenger dialogue pagination not... paginating

## 1.1.0 - 2026-09-18 Day 7 of development. Project send to the teacher, waiting our score

### Added
 - User Tracks Function, allow the player to load his own songs to each radio station
 - Pause hint on the tutorial

### Fixed
 - Leftover debug prints
 - Not having invincibility on the tutorial

## 1.0.0 - 2026-09-17 Day 6 of development

### Added
 - Passenger dialogues for knowing where it's going and his music taste
 - HUD for reading the Passenger dialogue, knowing if he's/she's happy and seeing him on the rearview
 - TypeWriterTextBox, inherits from Gale.ui.TextBox and displays the text letter by letter for easier reading, and plays a blip sounds.
 - Tutorial GameState and Strategy for a controlled enviroment where to learn about the game
 - MessageBox state for display texts with a TypeWriterTextBox
 - Fullscreen via F11

### Changed
 - Make GameOverState use a MessageBox instead of making his own panel

### Fixed
 - Remove unexpected collision in the middle of the city

## 1.0.0-beta - 2026-09-16 Day 5 of development

### Added
 - All variety of sounds, all from free from copyright sources. From [Pixabay](https://pixabay.com/es/) and [OpenGameArt](https://opengameart.org/). Includes:
    - Engine sounds
    - Crash sounds
    - Menu Sounds
    - More music
 - Arrow pointing towards the desination of the active passenger
 - Mouse particles
 - Make the car emit particles displaing his damage
 - Rest of the game states. Includes:
    - Opening
    - Title
    - Records
    - Select Mode
    - Pause
    - And several menus
 - Disconnect Gamemode logic from PlayState via Strategy on game_modes
 - Add 3 game modes, WorkDay, Arcade and Zen
 - Game saves via Gale.save, used for saving WorkDay mode games (For coming back later) and records

### Fixes
 - RadioTuner system, making it data-oriented
 - Command Pattern use on Taxi and RadioTuner
 - Radio marker visuals
 - Visual transitions between states
 - RadiotTuner visuals
 - Traffic Cars spinning when crashed or run out of nodes

## 1.0.0-alpha4 - 2026-09-15 Day 4 of development

### Added
 - Change all entity physics to Gale.Physics in order to allow for more freedom
 - Add Traffic Cars to the city
 - Add Particle Emitter, a manager for Gale.ParticleSystem disconnecting the particle behaivour from the entity that produces them
 - Add Particles for a lots of effecs
 - Initial Vibe Mode, allowing for drifting
 - Debug physics renders

### Deprecated
 - CollidableMixinClass

## 1.0.0-alpha3 - 2026-09-14 Day 3 of development

### Added
 - Design half of the city
 - Add initial radio system with free from copyright music

## 1.0.0-alpha2 - 2026-09-13 Day 2 of development

### Added
 - Basic passenger behaviour
 - passenger textures made by [vimlark](https://vimlark.itch.io/town-asset-pack-16x16) on itch.io
 - Change tilemap rendering from Gale's default to a per-layer rendering, allowing for overheads
 - Make base of buildings solid
 - "Mario sunshine shadow" for when the car is behind a building
 - Add some props
 - Start designing the radio UI

## 1.0.0-alpha1 - 2026-09-12 Day 1 of development

### Added
- Car movement by mouse controls and brake with "X", car properties defined by a definitions file
- Basic city tilemap made in tiled for testing driving
- Basic screen title state
- Fill cars and passengers definitions with basic data for testing
- Some cars textures by [Kia](https://kia.itch.io/32x32-car-sprites) on itch.io
- City tileset made by [nyknck](https://nyknck.itch.io/citypackpixelart) on itch.io

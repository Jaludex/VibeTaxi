Notable changes on the project will be documented here

# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), version format by [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.1.0 - 2026-09-18 Day 7 of development

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

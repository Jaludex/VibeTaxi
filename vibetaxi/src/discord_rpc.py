"""
Discord Rich Presence (RPC) integration for VibeTaxi.
Runs asynchronously in a background daemon thread to ensure the 60 FPS
game loop is never blocked by Discord IPC connection or socket timeouts.
"""

import time
import threading
from typing import Any, Dict, Optional

import settings
from src import config

try:
    from pypresence import Presence
    from pypresence.exceptions import (
        DiscordNotFound,
        PipeClosed,
        InvalidID,
        DiscordError,
    )
    PYPRESENCE_AVAILABLE = True
except ImportError:
    PYPRESENCE_AVAILABLE = False
    Presence = None
    DiscordNotFound = Exception
    PipeClosed = Exception
    InvalidID = Exception
    DiscordError = Exception


class DiscordRPCManager:
    """
    Manages Discord Rich Presence via pypresence on a background daemon thread.
    Handles connection errors, reconnection backoff, and IPC rate limiting.
    """

    def __init__(self, client_id: Optional[str] = None) -> None:
        self.client_id: str = str(
            client_id or getattr(settings, "DISCORD_CLIENT_ID", "1558733170730344582")
        )
        self._enabled: bool = bool(config.get("discord_rpc", True))
        self._presence: Optional[Presence] = None
        self._is_connected: bool = False
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._lock: threading.Lock = threading.Lock()

        self._pending_activity: Optional[Dict[str, Any]] = None
        self._last_sent_activity: Optional[Dict[str, Any]] = None
        self._last_sent_time: float = 0.0
        self._next_connect_attempt: float = 0.0
        self._min_update_interval: float = 3.5  # Seconds between IPC updates

        self._button_url: str = "https://jaludex.itch.io/vibe-taxi"
        self._button_label: str = "View on itch.io"
        self._session_start: int = int(time.time())

    def start(self) -> None:
        """Start the background worker thread."""
        if not PYPRESENCE_AVAILABLE or self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._worker_loop,
            name="DiscordRPCWorker",
            daemon=True,
        )
        self._thread.start()

    def close(self) -> None:
        """Shutdown the worker thread and close the Discord IPC connection."""
        self._running = False
        if self._presence and self._is_connected:
            try:
                self._presence.clear()
                self._presence.close()
            except Exception:
                pass
            self._presence = None
            self._is_connected = False

    def set_enabled(self, enabled: bool) -> None:
        """Dynamically enable or disable Discord Rich Presence."""
        with self._lock:
            self._enabled = enabled
            if not enabled and self._presence and self._is_connected:
                try:
                    self._presence.clear()
                except Exception:
                    pass

    def _worker_loop(self) -> None:
        """Background thread loop handling connection and periodic updates."""
        while self._running:
            now = time.time()

            # If user disabled Discord RPC in options
            if not self._enabled:
                if self._is_connected and self._presence:
                    try:
                        self._presence.clear()
                        self._presence.close()
                    except Exception:
                        pass
                    self._presence = None
                    self._is_connected = False
                    self._last_sent_activity = None
                time.sleep(0.5)
                continue

            # If not connected, attempt connection with backoff
            if not self._is_connected:
                if now >= self._next_connect_attempt:
                    self._try_connect()
                time.sleep(0.5)
                continue

            # Connected: check if there is an activity update to send
            activity_to_send = None
            with self._lock:
                if self._pending_activity is not None:
                    # Compare relevant fields to see if payload actually changed
                    if self._pending_activity != self._last_sent_activity:
                        if (now - self._last_sent_time) >= self._min_update_interval:
                            activity_to_send = dict(self._pending_activity)

            if activity_to_send is not None:
                self._send_update(activity_to_send)

            time.sleep(0.25)

    def _try_connect(self) -> None:
        """Attempt to connect to Discord IPC."""
        try:
            if self._presence is None:
                self._presence = Presence(self.client_id)
            self._presence.connect()
            self._is_connected = True
            self._last_sent_time = 0.0
            self._last_sent_activity = None
        except (DiscordNotFound, ConnectionRefusedError, FileNotFoundError, OSError):
            self._is_connected = False
            self._next_connect_attempt = time.time() + 15.0
        except Exception:
            self._is_connected = False
            self._next_connect_attempt = time.time() + 15.0

    def _send_update(self, activity: Dict[str, Any]) -> None:
        """Send presence activity to Discord."""
        try:
            if self._presence and self._is_connected:
                self._presence.update(**activity)
                self._last_sent_activity = activity
                self._last_sent_time = time.time()
        except (PipeClosed, ConnectionResetError, BrokenPipeError, DiscordError, OSError):
            # Discord was closed or connection dropped
            self._is_connected = False
            self._presence = None
            self._next_connect_attempt = time.time() + 15.0
        except Exception:
            self._is_connected = False
            self._presence = None
            self._next_connect_attempt = time.time() + 15.0

    def update_from_state(self, current_state: Any) -> None:
        """
        Extract activity details from the currently active game state
        and stage them for the worker thread.
        """
        if not PYPRESENCE_AVAILABLE or not self._running or current_state is None:
            return

        state_name = current_state.__class__.__name__
        details = "VibeTaxi"
        state = "Driving around"
        large_image = "logo"
        large_text = "VibeTaxi"
        small_image: Optional[str] = None
        small_text: Optional[str] = None

        if state_name == "PlayState":
            strategy = getattr(current_state, "game_rule_strategy", None)
            strat_name = strategy.__class__.__name__ if strategy else ""

            if strat_name == "WorkdayStrategy":
                day = int(getattr(strategy, "day", 1))
                money = float(getattr(strategy, "money", 0.0))
                fee = float(getattr(strategy, "fee", 80.0))

                details = f"Workday - Day {day}"
                pax = getattr(current_state, "active_passenger", None)
                if pax is not None:
                    pax_def = getattr(pax, "definition", {})
                    pax_name = pax_def.get("name", "Passenger")
                    state = f"Carrying {pax_name} | ${money:.0f} earned"
                else:
                    state = f"Cruising | ${money:.0f} / Goal ${fee:.0f}"

                small_image = "workday"
                small_text = f"Day {day}"

            elif strat_name == "ArcadeStrategy":
                score = int(getattr(strategy, "score", 0))
                delivered = int(getattr(strategy, "passengers_delivered", 0))

                details = "Arcade Mode"
                state = f"Score: {score} | Passengers: {delivered}"

                small_image = "arcade"
                small_text = "Arcade"

            elif strat_name == "ZenStrategy":
                details = "Zen Mode"
                state = "Cruising the city (No limits)"
                small_image = "zen"
                small_text = "Zen Mode"

            else:
                details = "In-game"
                state = "Driving through the city"

        elif state_name == "TutorialPlayState":
            details = "Tutorial"
            state = "Learning the ropes"

        elif state_name == "PauseState":
            details = "Paused"
            state = "Taking a break"

        elif state_name == "TitleScreenState":
            details = "Main Menu"
            state = "Selecting destination"

        elif state_name == "ModeSelectionState":
            details = "Mode Selection"
            state = "Choosing a game mode"

        elif state_name in ("OptionsState", "LanguageSelectionState"):
            details = "Settings"
            state = "Tuning options"

        elif state_name == "RecordsState":
            details = "Hall of Fame"
            state = "Checking top scores"

        elif state_name == "EndOfDayState":
            day = int(getattr(current_state, "day", 1))
            money = float(getattr(current_state, "money", 0.0))
            details = f"End of Day {day}"
            state = f"Earnings: ${money:.0f}"

        elif state_name == "GameOverState":
            details = "Game Over"
            state = "Shift ended"

        elif state_name == "NewRecordState":
            details = "New High Score!"
            state = "Registering name in Hall of Fame"

        elif state_name == "OpeningState":
            details = "Starting up"
            state = "Watching intro"

        payload: Dict[str, Any] = {
            "details": details,
            "state": state,
            "large_image": large_image,
            "large_text": large_text,
            "start": self._session_start,
            "buttons": [
                {
                    "label": self._button_label,
                    "url": self._button_url,
                }
            ],
        }

        if small_image is not None:
            payload["small_image"] = small_image
            if small_text:
                payload["small_text"] = small_text

        with self._lock:
            self._pending_activity = payload

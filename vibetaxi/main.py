import os
import sys
import traceback

def main():
    try:
        from src.VibeTaxi import VibeTaxi
        game = VibeTaxi()
        game.exec()
    except Exception as e:
        err_msg = traceback.format_exc()
        print("CRITICAL ERROR IN VIBETAXI:")
        print(err_msg)

        try:
            import androidembed
            androidembed.log(f"CRITICAL ERROR: {err_msg}")
        except Exception:
            pass

        # Write crash logs to reachable paths
        for log_dir in [
            os.environ.get("ANDROID_PRIVATE", "."),
            os.environ.get("ANDROID_ARGUMENT", "."),
            "/data/data/org.whiteboxstudio.vibetaxi/files",
            "/sdcard",
            "/storage/emulated/0",
            ".",
        ]:
            try:
                crash_file = os.path.join(log_dir, "vibetaxi_crash.log")
                with open(crash_file, "w") as f:
                    f.write(err_msg)
            except Exception:
                pass

        # Render emergency error screen on Android display if possible
        try:
            import pygame
            if not pygame.display.get_init():
                pygame.display.init()
            if not pygame.font.get_init():
                pygame.font.init()

            screen = pygame.display.get_surface()
            if screen is None:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

            screen.fill((40, 10, 10))
            font = pygame.font.Font(None, 24)
            y = 20
            header = font.render("VibeTaxi Crash on Startup:", True, (255, 100, 100))
            screen.blit(header, (20, y))
            y += 35

            for line in err_msg.splitlines()[-18:]:
                txt = font.render(line[:85], True, (255, 255, 255))
                screen.blit(txt, (20, y))
                y += 24

            pygame.display.flip()
            pygame.time.wait(12000)
        except Exception:
            pass

        raise


if __name__ == "__main__":
    main()

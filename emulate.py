from time import sleep

import pygame
from dotenv import load_dotenv

from controller import Controller
from shared import Runner


def main():
    load_dotenv()

    controller = Controller()

    runner = Runner(controller.jobs())

    pygame.init()
    screen = pygame.display.set_mode((250, 122))
    pygame.display.set_caption("Desk Controller Emulator")
    image = pygame.image.load(controller.current_display())
    screen.blit(image, (0, 0))
    pygame.display.flip()

    def handle_click(x_coord: int, y_coord: int):
        print(f"Clicked at ({x_coord}, {y_coord})")

        result = controller.touch_event(x_coord, y_coord, 0)
        if result is not None:
            new_image = pygame.image.load(result.display_path)
            screen.blit(new_image, (0, 0))
            pygame.display.flip()

    try:
        running = True
        while running:
            pending_update = controller.pending_update()
            if pending_update is not None:
                if pending_update.display_path != "":
                    new_image = pygame.image.load(pending_update.display_path)
                    screen.blit(new_image, (0, 0))
                    pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    handle_click(x, y)

            runner.run_pending()
            sleep(0.1)
    except KeyboardInterrupt:
        print("cleaning up")
        for app in controller.apps:
            app.app.clean_up()

    pygame.quit()
    for app in controller.apps:
        app.app.clean_up()


if __name__ == "__main__":
    main()

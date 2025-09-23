from typing import Dict, Tuple, List, Any, Callable

import traceback


RESET = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
BLUE = "\033[34m"
CYAN = "\033[36m"

CLEAR_SCREEN = "\033[2J"
CURSOR_HOME = "\033[H"


class DevMenu:
    def __init__(
        self,
        actions: Dict[
         str, Tuple[Callable[..., Any], Tuple[Any, ...], Dict[Any, Any]]
        ],
        title: str = "Dev Menu",
        message_lines: int = 5
    ):
        self.actions = actions
        self.title = title
        self.message_lines = message_lines
        self.messages: List[str] = []

    def show_menu(self) -> None:
        print(f"{CURSOR_HOME}{CLEAR_SCREEN}", end="")
        print(f"{BOLD}{YELLOW}=== {self.title} ==={RESET}")
        for key, (desc, fnc, args, kwargs) in self.actions.items():
            print(f"{CYAN}{key}) {desc or fnc.__name__}{RESET}")
        print(f"{CYAN}q) Quit{RESET}")
        print("\n--- Messages ---")
        # show last message_lines messages
        for msg in self.messages[-self.message_lines:]:
            print(msg)
        for _ in range(self.message_lines - len(self.messages[-self.message_lines:])):
            print()

    def log(self, msg: str) -> None:
        self.messages.append(str(msg))
        msgs_to_show = self.messages[-self.message_lines:]
        menu_height = len(self.actions) + 3  # title + q + "--- Messages ---"
        print(f"\033[{menu_height}H", end="")
        for line in self.messages[-self.message_lines:]:
            print(f"{line}\033[K")
        for _ in range(self.message_lines - len(msgs_to_show)):
            print("\033[K")

    def run_action(
     self,
     fnc: Callable[..., Any],
     args: Tuple[Any, ...] = (),
     kwargs: Dict[Any, Any] = {}) -> None:
        """Run function in 'full screen', temporarily suspending menu."""
        print(f"{CURSOR_HOME}{CLEAR_SCREEN}", end="")
        print(f"{BOLD}{YELLOW}=== Running {fnc.__name__} ==={RESET}\n")
        try:
            fnc(*args, **kwargs)
        except Exception as e:
            print(f"{RED}Error in {fnc.__name__}: {e}{RESET}")
            print(traceback.format_exc())
        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

    def run(self) -> None:
        while True:
            self.show_menu()
            choice = input(f"{BLUE}Choose an option: {RESET}").strip().lower()
            if choice == "q":
                self.log(f"{GREEN}Exiting menu...{RESET}")
                break
            if choice in self.actions:
                _, fnc, args, kwargs = self.actions[choice]
                self.run_action(fnc, args, kwargs)
                self.log(f"{GREEN}{fnc.__name__} finished.{RESET}")
            else:
                self.log(f"{RED}Invalid choice. Try again.{RESET}")

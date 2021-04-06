"""
Linus Eriksson
m5-uppgift-P2-wallet-tx-python
BBT200
"""

from PrivateKey import CoinKey

ACTION_CHOICES = {
    1: "Create key safe",
    2: "Create key by seed",
    3: "Set key by value",
    0: "Exit program"
}


def end_program():
    print("Exiting, thank you for using and have a great day!")
    return False


def _print_action_info():
    print("Select action:")
    for number, action in ACTION_CHOICES.items():
        print(f"{number}. {action}")


def _print_key_info(key: CoinKey):
    key.generate_public_key()
    print(f"Generated key info:")
    print(str(key))


def create_safe_key():
    key = CoinKey()
    key.generate_private_safe()
    _print_key_info(key)
    return True


def create_key_by_seed():
    seed = None
    while seed is None:
        print("Enter seed:")
        try:
            seed = int(input())
        except ValueError:
            print("Enter a valid integer seed!")
    key = CoinKey()
    key.generate_private_with_seed(seed)
    _print_key_info(key)
    return True


def set_key_by_value():
    key_Val = None
    while key_Val is None:
        print("Enter key value:")
        try:
            key_Val = int(input())
        except ValueError:
            print("Enter a valid integer value!")
    key = CoinKey()
    key.set_private(key_Val)
    _print_key_info(key)
    return True


def _system_loop():
    actions = {
        1: create_safe_key,
        2: create_key_by_seed,
        3: set_key_by_value,
        0: end_program
    }
    print("*" * 64)
    while True:
        _print_action_info()
        selection = input()
        keep_going = True
        try:
            keep_going = actions[int(selection)]()
        except KeyError:
            print(f"No action mapped for selection {selection}")
        except ValueError:
            print("Input integer for selection")
        if not keep_going:
            break
        print("*" * 64 + "\n")


def main():
    _system_loop()


if __name__ == '__main__':
    main()
    exit(0)

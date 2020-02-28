from aiogram.utils.helper import Helper, HelperMode, ListItem


class UserStates(Helper):
    mode = HelperMode.snake_case

    MAIN_MENU = ListItem()
    ADMIN_MENU = ListItem()
    ADMIN_ADD = ListItem()
    ADMIN_BROADCAST = ListItem()
    WAIT_FOR_NAME = ListItem()
    WAIT_FOR_RESULT = ListItem()
    WAIT_FOR_VERIFIED = ListItem()


if __name__ == '__main__':
    print(UserStates.all())

from telebot import AdvancedCustomFilter


class ChatFilterCallback(AdvancedCustomFilter):
    """
    Check whether chat_id corresponds to given chat_id.

    Example:
    @bot.message_handler(chat_id=[99999])
    """

    key = 'chat_id_callback'

    def check(self, callback, text):
        return callback.from_user.id in text
import logging
import os

class BackupHandler:
    def __init__(self, path, message_length):
        self.path = path
        self.messages = []
        self.message_length = message_length

        if not os.path.exists(path):
            with open(path, "wb") as f:
                pass

        with open(path, "rb") as f:
            data = bytearray(f.read())
            print(f"{os.path.getsize(path)/self.message_length} messages detected in the backup file.")

            self.messages = []
            if not (len(data)/self.message_length).is_integer():
                return

            for _ in range(0, int(round(len(data)/self.message_length))):
                self.messages.append(data[:self.message_length])
                del data[:self.message_length]
            print(len(self.messages))

    def backup_messages(self, data):
        self.messages.extend(data)
        try:
            with open(self.path, "ab") as f:
                for msg in data:
                    f.write(msg)
        except Exception as e:
            print("Failed to save message to the file" + str(e))

    def _clear_file(self):
        try:
            open(self.path, 'w').close()
            logging.debug("Backup file cleared")
        except Exception as e:
            logging.warning("Failed to clear backup file" + str(e))

    def get_unsent_messages(self, number_of_messages = 1):
        if len(self.messages) >= number_of_messages:
            popped_messages = self.messages[0: number_of_messages]
            self.messages = self.messages[number_of_messages:]
            if not self.messages:
                self._clear_file()
            return popped_messages
        elif len(self.messages) > 0:
            popped_messages = self.messages[:]
            self.messages = []
            self._clear_file()

            return popped_messages
        else:
            return []

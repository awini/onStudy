import sqlalchemy.types as types


class Choice(types.TypeDecorator):

    impl = types.String

    def __init__(self, choices: dict, **kwargs):
        self.choices = choices  # key for long, value for short form
        self.__set_reverse_choices()
        super().__init__(**kwargs)

    def __set_reverse_choices(self):
        self.reverse_choices = {value: key for key, value in self.choices.items()}

    def process_bind_param(self, value, dialect):
        # value from user input
        return self.choices[value]


    def process_result_value(self, value, dialect):
        # value from DB
        return self.reverse_choices[value]
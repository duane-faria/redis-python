ARRAY_IDENTIFIER: str = '*'
SIMPLE_STRING_IDENTIFIER: str = '+'
BULK_STRING_IDENTIFIER: str = '$'
ENCODING_DIVIDER="\r\n"

class RESPParser:
    def __init__(self, data):
        self.data = data
    
    def parse(self):
        data_identifier = self.data[0]

        if data_identifier == ARRAY_IDENTIFIER:
            return self._parse_array()

        if data_identifier == SIMPLE_STRING_IDENTIFIER:
           return self._parse_simple_string()

        return ['', '']

    def _parse_array(self):
        broken_data = self.data.split('\r\n')
        filtered_data = [value for index, value in enumerate(broken_data) if self._filter_values(value, index)]
        return filtered_data

    def _parse_simple_string(self):
        command = self.data.replace("\r\n", "")
        return [command[1:], '']

    def _filter_values(self, value: str, index: int) -> bool:
        return index > 0 and len(value) > 0 and value[0] != '$'
    
    
class RESPEncoder:
    def __init__(self):
        pass

    @staticmethod
    def encode(value: str | None) -> bytes:

        if isinstance(value, str) and len(value) <= 4:
           return RESPEncoder.simple_string_encode(value)

        if isinstance(value, str):
            return RESPEncoder.bulk_string_encode(value)

        if value is None:
            return f"{BULK_STRING_IDENTIFIER}-1\r\n".encode("utf-8")

    @staticmethod
    def bulk_string_encode(value: str | list):
        length = len(value.encode("utf-8"))
        return f"{BULK_STRING_IDENTIFIER}{length}\r\n{value}\r\n".encode("utf-8")

    @staticmethod
    def simple_string_encode(value: str):
        return f"{SIMPLE_STRING_IDENTIFIER}{value}\r\n".encode("utf-8")

    @staticmethod
    def array_encode(value: str | list[str]):
        if isinstance(value, str):
            array_length = 1
            return f"{ARRAY_IDENTIFIER}{array_length}{ENCODING_DIVIDER}{BULK_STRING_IDENTIFIER}{len(value)}{ENCODING_DIVIDER}{value}{ENCODING_DIVIDER}".encode("utf-8")

        if isinstance(value, list):
            array_length = len(value)
            items = []

            for item in value:
                items.append(f'{BULK_STRING_IDENTIFIER}{len(item)}')
                items.append(item)

            return f"{ARRAY_IDENTIFIER}{array_length}{ENCODING_DIVIDER}{ENCODING_DIVIDER.join(items)}{ENCODING_DIVIDER}".encode("utf-8")      
        

#  python3 -m app.resp_handlers.py
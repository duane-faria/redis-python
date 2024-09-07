import re

ARRAY_IDENTIFIER: str = '*'
SIMPLE_STRING_IDENTIFIER: str = '+'
BULK_STRING_IDENTIFIER: str = '$'
ENCODING_DIVIDER="\r\n"

class RESPParser:
    def __init__(self, data: bytes):
        self.data = data.decode('utf-8')

    def get_all_array_positions(self):
        asterisks = [m.start() for m in re.finditer(r'\*', self.data)]
        return asterisks

    def parse(self):
        data_identifier = self.data[0]
        response = ['', '']
        if data_identifier == ARRAY_IDENTIFIER:
            has_multiple_arrays = len(self.get_all_array_positions()) > 1
            if not has_multiple_arrays:
                response = self._parse_array()
            else:
                print('caiu no else do array')
                exclude_list = [ARRAY_IDENTIFIER, BULK_STRING_IDENTIFIER]
                elements: list[str] = self.data.split('\r\n')
                message_elements = []
                sub_list = []
                counter = 0
                for element in elements:
                    if not len(element) > 0: # if empty skip
                        continue

                    element_has_identifier = element[0] in exclude_list
                    if element[0] == ARRAY_IDENTIFIER and counter > 1:
                        message_elements.append(sub_list)
                        sub_list = []
                    if not element_has_identifier:
                        sub_list.append(element)
                    counter += 1

                message_elements.append(sub_list)
                response = message_elements
                print(response)
        if data_identifier == SIMPLE_STRING_IDENTIFIER:
           response = self._parse_simple_string()

        return response

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
# Uncomment this to pass the first stage
import socket
import threading

# constants
ARRAY_IDENTIFIER: str = '*'
STRING_IDENTIFIER: str = '+'
BULK_STRING_IDENTIFIER: str = '$'
PONG = "+PONG\r\n".encode("utf-8")


# TODO solve some random issue here
def filter_values_from_array_of_resp_strings(tuple_list: tuple[int, str]):
    arr = list(tuple_list)

    index = arr[0]
    value = arr[1]

    return index > 0 and len(value) > 0 and value[0] != '$'


def parse_resp(data: str) -> [list, str]:
    data_identifier = data[0]

    if data_identifier == ARRAY_IDENTIFIER:
        broken_data = data.split('\r\n')
        print(broken_data, 'broken_data')
        x = filter(filter_values_from_array_of_resp_strings, enumerate(broken_data))
        tuple_list = list(x)
        print(tuple_list, 'tuple_list')
        return [item[1] for item in tuple_list]

    if data_identifier == STRING_IDENTIFIER:
        command = data.replace("\r\n", "")
        return [command[1:], '']

    return ['', '']


def encode_resp(value):
    encoded_str = ''
    if isinstance(value, str):
        encoded_str = f"{BULK_STRING_IDENTIFIER}{len(value)}\r\n{value}\r\n"

    return encoded_str.encode("utf-8")


def wait_for_messages(conn, address):
    # wait for client
    with conn:
        while True:
            encoded_message = conn.recv(1024)

            command_and_payload = parse_resp(encoded_message.decode('utf-8'))
            response = ''
            command = command_and_payload[0]
            print(command_and_payload, 'command_and_payload')

            if command.lower() == 'ping':
                response = PONG
            if command.lower() == 'echo':
                print('echo command', encode_resp(command_and_payload[1]))
                response = encode_resp(command_and_payload[1])
                print(response, 'response')
            conn.send(response)


def main():
    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        conn, address = server_socket.accept()
        threading.Thread(target=wait_for_messages, args=(conn, address)).start()


if __name__ == "__main__":
    main()

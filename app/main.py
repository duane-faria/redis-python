from app.redis import RedisServer
from app.utils import HandleCliParams

def main():
    cli_params = HandleCliParams().execute()
    port = cli_params['port'] or 6379
    replica = cli_params['replica'] # it means the redis server is a slave if filled

    RedisServer(host='localhost', port=port, replica=replica).start()

if __name__ == "__main__":
    main()


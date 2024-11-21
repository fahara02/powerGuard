from powerguard.gui import setGui
from server import Server

server = Server()


def main():
    print("Hello from powerguard!")
    setGui()
    server.start_server()


if __name__ == "__main__":
    main()

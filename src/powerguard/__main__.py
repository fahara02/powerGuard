from powerguard.gui import setGui
from server import serve


def main():
     print("Hello from powerguard!")
     serve()   
     setGui()


if __name__ == "__main__":
    main()

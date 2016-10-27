"""Application entry point."""
import argparse
import logging

from pytocl.protocol import Client


def main():
    """Main entry point of application."""
    parser = argparse.ArgumentParser(description='Client for TORCS racing car simulation with SCRC '
                                                 'network server.')
    parser.add_argument('--hostname', help='Racing server host name.', default='localhost')
    parser.add_argument('--port', help='Port to connect, 3001 - 3010 for clients 1 - 10.',
                        type=int, default=3001)
    parser.add_argument('-v', help='Debug log level.', action='store_true')
    args = parser.parse_args()

    # switch log level:
    if args.v:
        level = logging.WARNING
    else:
        level = logging.WARNING
    del args.v
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)7s %(name)s %(message)s")

    # start client loop:
    client = Client(**args.__dict__)
    client.run()


if __name__ == '__main__':
    main()

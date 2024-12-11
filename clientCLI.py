import db_functions
import time
from tcpModem import types


if __name__ == '__main__':
    print('')
    print('#########################################')
    print('#  IMBR - It must be received')
    print('#  Bob KD9YQK - https://www.kd9yqk.com/')
    print('#########################################')

    done = False
    while not done:
        a = input('\nCommand (Type ? for help) > ').lower()

        if a in ['?', 'h', 'help']:
            print('\nc, create - Create a new post.')
            print('g, get - Get newest posts for callsign')
            print('?, h, help - Show this help message.')
            print('q, quit, exit - Close this IMBR client.')

        elif a in ['q', 'quit', 'exit']:
            print('\nClosing IMBR Client')
            done = True

        elif a in ['c', 'create']:
            print('\n Enter your callsign')
            b = input('> ')
            if b == '':
                print('\n Error - A callsign is needed.')
            else:
                print('\nEnter the message for your post.')
                c = input('> ')
                if c == '':
                    print('\n Error - You need to type a message.')
                else:
                    t = int(time.time())
                    db_functions.add_blog(t, b.upper(), c.upper())
                    db_functions.add_outgoing_post(types.ADD_TARGET_BLOG, t, b.upper(), c.upper())

        elif a in ['g', 'get']:
            print('\nEnter a callsign to lookup.')
            b = input('> ')
            if b == '':
                print('Error - A callsign is needed.')
            else:
                posts = db_functions.get_callsign_blog(b.upper(), 5)
                if len(posts) == 0:
                    print(f'\nThere are no posts for {b} in this stations database.')
                else:
                    num = 1
                    for p in posts:
                        print(f'\n# Post {num} of {len(posts)}')
                        print(f'# {p["callsign"]} - {p["local"]}')
                        print(f'{p["msg"]}')
                        num += 1

        else:
            print(f'Error - Unknown Command - {a}')

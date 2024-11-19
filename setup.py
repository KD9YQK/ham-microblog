import db_functions

if __name__ == '__main__':
    print()
    print('What is your callsign?')
    callsign = input("> ")
    print(f'Welcome {callsign}!')
    print()
    print('Enable JS8Call Modem?')
    j = input("y/n (default:n)> ")
    if j.lower() in ['y', 'yes']:
        j = True
        print('JS8Call Modem Enabled')
    else:
        j = False
        print('JS8Call Modem Disabled')
    print()
    print('Enable APRS Modem?')
    a = input("y/n (default:n)> ")
    if a.lower() in ['y', 'yes']:
        a = True
        print('APRS Modem Enabled')
    else:
        a = False
        print('APRS Modem Disabled')
    print()
    print('Enable TCP/IP Modem?')
    t = input("y/n (default:n)> ")
    if t.lower() in ['y', 'yes']:
        t = True
        print('TCP/IP Modem Enabled')
    else:
        t = False
        print('TCP/IP Modem Disabled')
    print()
    print('How should we display time?\n1:GMT\n2:Local')
    tm = input("1-2 (default:1)> ")
    if tm == '2':
        tm = 'local'
        print('Time will be displayed in Local Time')
    else:
        tm = 'gmt'
        print('Time will be displayed in GMT Time')
    db_functions.build_db()
    db_functions.set_settings(callsign.upper(), j, a, t, tm)
    print('Setup Complete')

    exit()

    t = db_functions.get_time()
    db_functions.add_blog(t, "KD9YQK",
                          "Today a man knocked on my door and asked for a small donation towards the local swimming "
                          "pool. I gave him a glass of water.")
    db_functions.add_blog(t - 100, "KD9YQK",
                          "Ham and Eggs: A day's work for a chicken, a lifetime commitment for a pig.")
    db_functions.add_blog(t - 150, "KD9UEG",
                          "What do you call a dog with no legs? Doesn't matter what you call him, he's not coming.")
    db_functions.add_blog(t - 1150, "KD9UEG", "Always identify who to blame in an emergency.")
    db_functions.add_blog(t - 140, "KM6LYW",
                          "My wife just found out I replaced our bed with a trampoline; she hit the roof.")
    db_functions.add_blog(t - 340, "KM6LYW",
                          "Smoking will kill you... Bacon will kill you... But, smoking bacon will cure it.")
    db_functions.add_blog(t - 1250, "KD9YQK", "A liberal is just a conservative that hasn't been mugged yet.")
    l = []
    for i in range(0, 5000):
        l.append({"time": t - 200 - i, "callsign": "KD9YQK", "msg": f"Test Message #{str(i + 1)}"})
    db_functions.bulk_add_blog(l)

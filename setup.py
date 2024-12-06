import db_functions

if __name__ == '__main__':
    print('')
    print('#########################################')
    print('#  Ham Microblog Setup')
    print('#  Bob KD9YQK - http://www.kd9yqk.com/')
    print('#########################################')
    print()
    print('What is your callsign?')
    callsign = input("> ")
    print(f'  * Welcome {callsign.upper()}!')
    print()

    print('Enable JS8Call Modem?')
    js8modem = False
    js8host = '127.0.0.1'
    js8port = 2442
    js8group = '@BLOG'
    i = input("y/n (default:n)> ")
    if i.lower() in ['y', 'yes']:
        js8modem = True
        print('  * JS8Call Modem Enabled')
        print('JS8Call TCP Address?')
        i = input(f"(default:{js8host})> ")
        if i == "":
            pass
        elif i.split('.') == 4:
            js8host = i
        else:
            print(f'  * Error - Cannot parse IP')
        print(f'  * JS8Call IP set to {js8host}')
        print('JS8Call TCP Port?')
        i = input(f"(default:{js8port})> ")
        try:
            if i != '':
                js8port = int(i)
        except ValueError:
            print(f'  * Error - Not a valid number')
        print(f'  * JS8Call Port set to {js8port}')
        print('JS8Call Target Group?')
        i = input(f"(default:{js8group})> ")
        if i == "":
            pass
        elif i[:1] != "@":
            print(f'  * Error - Not a valid group name')
        else:
            js8group = i.upper()
        print(f'  * JS8Call Group set to {js8group}')
    else:
        print('  * JS8Call Modem Disabled')
    print()

    print('Enable APRS Modem?')
    aprsmodem = False
    aprshost = '127.0.0.1'
    aprsport = 8001
    aprs_ssid = 15
    lat = "4043.24N"
    lon = "07400.22W"
    i = input("y/n (default:n)> ")
    if i.lower() in ['y', 'yes']:
        aprsmodem = True
        print('  * APRS Modem Enabled')
        print('APRS TCP Address?')
        i = input(f"(default:{aprshost})> ")
        if i == "":
            pass
        elif len(i.split('.')) == 4:
            aprshost = i
        else:
            print(f'  * Error - Cannot parse IP')
        print(f'  * APRS IP set to {aprshost}')
        print('APRS TCP Port?')
        i = input(f"(default:{aprsport})> ")
        try:
            if i != '':
                aprsport = int(i)
        except ValueError:
            print(f'  * Error - Not a valid number')
        print(f'  * APRS Port set to {aprsport}')
        print('APRS SSID?')
        i = input(f"0-15 (default:{aprs_ssid})> ")
        try:
            if i != '':
                aprs_ssid = int(i)
        except ValueError:
            print(f'  * Error - Not a valid number')
        print('Latitude DDMM.SSN')
        i = input(f"example ({lat}))> ")
        if i != '':
            lat = i.upper()
        else:
            print(f'  * Error - Coordinates are required for APRS')
            exit()
        print('Longitude 0DDMM.SSW')
        i = input(f"example ({lon}))> ")
        if i != '':
            lon = i.upper()
        else:
            print(f'  * Error - Coordinates are required for APRS')
            exit()
        print(f'  * Latitude/Longitude set to {lat}/{lon}')
    else:
        print('  * APRS Modem Disabled')
    print()

    print('Enable TCP/IP Modem?')
    tcpmodem = False
    i = input("y/n (default:n)> ")
    if i.lower() in ['y', 'yes']:
        tcpmodem = True
        print('  * TCP/IP Modem Enabled')
    else:
        print('  * TCP/IP Modem Disabled')
    print()

    print('How should we display time?\n1:GMT\n2:Local')
    i = input("1-2 (default:1)> ")
    tm = 'gmt'
    if i == '2':
        tm = 'local'
        print('  * Time will be displayed in Local Time')
    else:
        print('  * Time will be displayed in GMT Time')
    db_functions.build_db()
    db_functions.set_settings(callsign.upper(), js8modem, js8host, js8port, js8group, aprsmodem, aprshost, aprsport,
                              aprs_ssid, tcpmodem, tm, lat, lon)
    print('Setup Complete')

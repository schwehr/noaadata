#!/usr/bin/env python


# Since 2010-Jul-13
# Connect to AISUser and watch how many messages it is receiving from the USCG


import datetime
import select
import socket
import time


def main():
    host_name = "localhost"
    port_num = 31414
    connected = False
    with open("aisuser-rate.log", "w") as o:
        start_time = time.time()
        while True:
            count = 0

            if count != 0:
                time.sleep(0.25)
            try:
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                soc.connect((host_name, port_num))
            except OSError as inst:
                print("soc connect failed:", str(inst))
            else:
                connected = True
                print("CONNECT to ", host_name, port_num)

            prev_time = time.time()
            rcv_count = 0
            while connected:
                count += 1
                if count % 10000 == 0:
                    print(
                        "inner_ListenThread:",
                        count,
                        datetime.datetime.now().strftime("%dT%H:%M:%S"),
                        "EST\tconnected:",
                        connected,
                    )
                if count % 100 == 0:
                    time.sleep(0.01)
                readersready, _outputready, _exceptready = select.select(
                    [
                        soc,
                    ],
                    [],
                    [],
                    0.1,
                )
                if len(readersready) == 0:
                    continue
                data = soc.recv(640)
                if len(data) == 0:
                    connected = False
                    print("DISCONNECT")
                    break

                now = time.time()
                dt = now - prev_time
                rcv_count += data.count("\r")

                if dt >= 1.0:
                    rate = rcv_count / dt
                    offset = now - start_time
                    o.write(f"{offset} {rate} {rcv_count} {now} {dt}\n")
                    o.flush()
                    if count % 5 == 0:
                        print(f"{offset} {rate} {rcv_count} {now}")
                    rcv_count = 0
                    prev_time = now


if __name__ == "__main__":
    main()

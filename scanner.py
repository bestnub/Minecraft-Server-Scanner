from unicodedata import name
from uuid import UUID
from sqlalchemy.orm import relationship
import random
import sys
import time
import masscan
from mcstatus import JavaServer
import json
import os
import math
import threading
import time
import argparse
import queue
import os
from sqlalchemy import Column, Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_DATABASE = os.getenv('DB_DATABASE')
DB_IP = os.getenv('DB_IP')
DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PW')

Base = declarative_base()


association_table = Table(
    "server_user",
    Base.metadata,
    Column("server_id", ForeignKey("server.id"), primary_key=True),
    Column("user_uuid", ForeignKey("user.uuid"), primary_key=True),
)


class Server(Base):
    __tablename__ = "server"
    id = Column(Integer, primary_key=True)
    ip = Column(String(15))
    desc = Column(String)
    maxUser = Column(Integer)
    versionProtocol = Column(String)
    versionName = Column(String)
    users = relationship(
        "User", secondary=association_table, back_populates="servers"
    )


class User(Base):
    __tablename__ = "user"
    uuid = Column(String, primary_key=True)
    name = Column(String)
    servers = relationship(
        "Server", secondary=association_table, back_populates="users"
    )


engine = create_engine(
    "mariadb://" + DB_USER + ":" + DB_PW + "@" + DB_IP + "/" + DB_DATABASE, echo=True, future=True)
Base.metadata.create_all(engine)


ipQ = queue.LifoQueue()


class myThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadID

    def run(self):
        print("Starting Thread " + self.name)
        while True:
            print_time(self.name, ipQ.get())


exitFlag = 0


def print_time(threadName, ip):
    if exitFlag:
        print("Exiting Thread " + threadName)
        threadName.exit()
    try:
        server = JavaServer(ip, 25565)
        status = server.status()
    except:
        print("Failed to get status of: " + ip)
    else:
        print("Found server: " + ip + " " + status.version.name +
              " " + str(status.players.online))
        playersString = "Palyer:"
        if status.players.sample is not None:
            for player in status.players.sample:
                player.id
                playersString += " "
                playersString += player.name
        print(playersString)


if __name__ == "__main__":

    threads = int(
        input('How many threads do you want to use? (Recommended 20): '))

    for i in range(threads):
        myThread(i).start()

        # create IP ranges
    A = list(range(1, 0xff))
    B = list(range(1, 0xff))
    random.shuffle(A)
    random.shuffle(B)
    ip_ranges = []
    for a in A:
        for b in B:
            ip_range = f"{a}.{b}.0.0/16"
            ip_ranges.append(ip_range)

    while True:
        random.shuffle(ip_ranges)
        for ip_range in ip_ranges:
            print(ip_range)
            try:
                mas = masscan.PortScanner()
                mas.scan(ip_range, ports='25565',
                         arguments='--max-rate 300000 --excludefile exclude.conf')
                scan_result = json.loads(mas.scan_result)
                # print(scan_result["scan"])
                # scanJobs = []
                for ip in scan_result["scan"]:
                    host = scan_result["scan"][ip]
                    if "tcp" == host[0]["proto"] and 25565 == host[0]["port"]:
                        # scanJobs.append(ip)
                        ipQ.put(ip)
                        # try:
                        #     server = JavaServer(ip, 25565)
                        #     status = server.status()
                        #     print("Server:")
                        #     print(f"Desc: {status.description}")
                        #     print(f"IP: {ip}")
                        #     print(
                        #         f"PalyerCount: {status.players.online}/{status.players.max}")
                        #     playersString = "Palyer:"
                        #     for player in status.players.sample:
                        #         playersString += " "
                        #         playersString += player.name
                        #     print(playersString)
                        #     print(
                        #         f"Version: {status.version.protocol} {status.version.name}")
                        #     print("-----")
                        # except:
                        #     print("Failed to get status of: " + ip)

            except OSError:
                print(f"{ip_range} masscan error")
        ipQ.join()
        print("done scanning")

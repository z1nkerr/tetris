import socket, time
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import sqlalchemy.exc
import sqlite3

main_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY, 1)
main_socket.bind(("192.168.1.115", 2222))
main_socket.setblocking(False)
main_socket.listen(5)
engine = create_engine("sqlite:///data.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()
s = Session()
class Player(Base):
    __tablename__ = "gamers"
    name = Column(String, primary_key=True)
    password = Column(String(250))
    score = Column(Integer, default=0)
    def __init__(self, name, passw):
        self.name = name
        self.password = passw
Base.metadata.create_all(engine)
print('Сокет создался')
players = []
run = True
while run:
    try:
        new_socket, addr = main_socket.accept() # принимаем входящие
        print('Подключился', addr)
        new_socket.setblocking(False)
        players.append(new_socket)

    except BlockingIOError:
        pass
    for sock in players:
        try:
            data = sock.recv(1024).decode()
            data = data[1:]
            data=data[:-1]
            data = data.split(',')
            if data[0] == 'final':
                data.remove('final')
                player = s.get(Player, data[0])
                if player.score < int(data[2]):
                    player.score = int(data[2])
                    s.merge(player)
                    s.commit()
            if data:
                player = Player(data[0], data[1])
                s.add(player)
                s.commit()
                sock.send("<0>".encode())
                print("Получил", data)
                sock.close()
                players.remove(sock)
        except sqlalchemy.exc.IntegrityError:
            s.rollback()
            player = s.get(Player, data[0])
            if data[1] == player.password:
                sock.send(f"<{player.score}>".encode())
            else:
                sock.send("<-1>".encode())
            sock.close()
            players.remove(sock)
        except:
            pass
    time.sleep(1)
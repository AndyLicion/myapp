from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.conf import settings
from django.core.cache import cache

class MultiPlayer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print('accept')


    async def disconnect(self, close_code):
        print('disconnect')
        await self.channel_layer.group_discard(self.room_name, self.channel_name)


    async def create_player(self, data):
        self.room_name = None
        start = 0;

        for i in range(start, 100000000): # 设定连接上就在缓存中只开一千个房间
            name = "room-%d" %(i)
            if not cache.keys(name) or len(cache.get(name)) < settings.ROOM_CAPACITY:
                self.room_name = name
                break

        if not self.room_name: # 所有房间全满了
            return

        if not cache.has_key(self.room_name):
            cache.set(self.room_name, [], 3600) # 创建房间有效期1小时

        for player in cache.get(self.room_name): # 发送创建该玩家消息
            await self.send(text_data=json.dumps({
                'event': "create_player",
                'uuid': player['uuid'],
                'username': player['username'],
                'photo': player['photo'],
            }))

        await self.channel_layer.group_add(self.room_name, self.channel_name)


        players = cache.get(self.room_name)
        players.append({
            'uuid': data['uuid'],
            'username': data['username'],
            'photo': data['photo']
        })
        cache.set(self.room_name, players, 3600) # 房间中最后一位玩家创建完之后更新房间有效期1小时

        await self.channel_layer.group_send( # 广播通知一个房间里的所有玩家都将该玩家在其显示的游戏窗口中创建出来
                self.room_name,
                {
                    'type': "group_send_event",
                    'event': "create_player",
                    'uuid': data['uuid'],
                    'username': data['username'],
                    'photo': data['photo']
                }
        )


    async def move_to(self, data):
        await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': "group_send_event",
                    'event': "move_to",
                    'uuid': data['uuid'],
                    'tx': data['tx'],
                    'ty': data['ty'],
                }
        )


    async def shoot_fireball(self, data):
        await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': "group_send_event",
                    'event': "shoot_fireball",
                    'uuid': data['uuid'],
                    'tx': data['tx'],
                    'ty': data['ty'],
                    'fireball_uuid': data['fireball_uuid'],
                }
        )


    async def attack(self, data):
        await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': "group_send_event",
                    'event': "attack",
                    'uuid': data['uuid'],
                    'attackee_uuid': data['attackee_uuid'],
                    'x': data['x'],
                    'y': data['y'],
                    'angle': data['angle'],
                    'damage': data['damage'],
                    'fireball_uuid': data['fireball_uuid'],
                }
        )


    async def blink(self, data):
        await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': "group_send_event",
                    'event': "blink",
                    'uuid': data['uuid'],
                    'tx': data['tx'],
                    'ty': data['ty'],
                }
        )


    async def group_send_event(self, data): # 通知除本窗口以外所有窗口玩家在其游戏窗口显示玩家的控制的结果
        await self.send(text_data=json.dumps(data))


    async def receive(self, text_data): # 接收到的一个窗口发送来的消息
        data = json.loads(text_data)
        event = data['event']
        if event == "create_player":
            await self.create_player(data)
        elif event == "move_to":
            await self.move_to(data)
        elif event == "shoot_fireball":
            await self.shoot_fireball(data)
        elif event == "attack":
            await self.attack(data)
        elif event == "blink":
            await self.blink(data);

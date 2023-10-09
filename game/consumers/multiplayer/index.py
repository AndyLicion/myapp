from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.conf import settings
from django.core.cache import cache

class MultiPlayer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = None

        for i in range(1000): # 设定连接上就在缓存中只开一千个房间
            name = "room-%d" %(i)
            if not cache.keys(name) or len(cache.get(name)) < settings.ROOM_CAPACITY:
                self.room_name = name
                break

        if not self.room_name:
            return

        await self.accept()
        print('accept')

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

    async def disconnect(self, close_code):
        print('disconnect')
        await self.channel_layer.group_discard(self.room_name, self.channel_name)


    async def create_player(self, data):
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
                'type': "group_create_player",
                'event': "create_player",
                'uuid': data['uuid'],
                'username': data['username'],
                'photo': data['photo']
            }
        )

    async def group_create_player(self, data): # 通知除本窗口以外所有窗口玩家在其游戏窗口中创建本玩家的控制副本
        await self.send(text_data=json.dumps(data))

    async def receive(self, text_data): # 接收到的广播消息
        data = json.loads(text_data)
        event = data['event']
        if event == "create_player":
            await self.create_player(data)

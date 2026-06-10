import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f'chat_{self.match_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Start score update simulation if it's not already running for this group
        # In a real app, this would be a separate process, but for simulation:
        if not hasattr(self.channel_layer, f'score_task_{self.match_id}'):
            setattr(self.channel_layer, f'score_task_{self.match_id}', True)
            asyncio.create_task(self.simulate_score_updates())

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        if not message:
            return

        # Generate a dummy username on the server side as requested
        username = f'User_{random.randint(1000, 9999)}'

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username
        }))

    # Method to handle score updates
    async def score_update(self, event):
        # Send score update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'score_update',
            'score_data': event['score_data']
        }))

    async def simulate_score_updates(self):
        """Simulates live score updates every 10 seconds."""
        runs = 0
        wickets = 0
        balls = 0
        score_history = []
        current_over_runs = 0
        recent_balls = []

        while True:
            await asyncio.sleep(10)
            
            # Simulate a ball
            ball_result = random.choice([0, 1, 2, 3, 4, 6, 'W'])
            
            if ball_result == 'W':
                wickets += 1
                recent_balls.append('W')
            else:
                runs += ball_result
                current_over_runs += ball_result
                recent_balls.append(ball_result if ball_result > 0 else '•')
            
            balls += 1
            if len(recent_balls) > 6:
                recent_balls.pop(0)

            overs = (balls // 6) + (balls % 6) / 10.0
            
            if balls % 6 == 0:
                score_history.append(current_over_runs)
                current_over_runs = 0
                if len(score_history) > 10:
                    score_history.pop(0)

            crr = (runs / balls * 6) if balls > 0 else 0.0
            
            score_data = {
                'total_runs': runs,
                'wickets': wickets,
                'overs': f"{overs:.1f}",
                'current_run_rate': f"{crr:.2f}",
                'target': 250,
                'required_run_rate': f"{(250 - runs) / (50 - overs) * 6:.2f}" if (50 - overs) > 0 else "0.00",
                'recent_balls': recent_balls,
                'score_history': score_history
            }

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'score_update',
                    'score_data': score_data
                }
            )

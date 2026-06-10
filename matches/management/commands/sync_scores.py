import time
import json
import random
import requests
from django.core.management.base import BaseCommand
from matches.models import Match
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Command(BaseCommand):
    help = 'Syncs live cricket scores from an external API or scraper'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting live score sync service...'))
        
        while True:
            try:
                active_matches = Match.objects.filter(is_live=True, category='LIVE_SPORTS')
                
                if not active_matches.exists():
                    self.stdout.write('No active live sports matches found. Waiting...')
                    time.sleep(30)
                    continue

                for match in active_matches:
                    self.stdout.write(f'Updating match: {match.title}')
                    
                    # In a real-world scenario, you would fetch data from an API here:
                    # response = requests.get(f'https://api.cricketdata.org/v1/match_stats?id={match.id}')
                    # data = response.json()
                    
                    # Since we don't have a specific API key/endpoint provided, 
                    # we implement a robust simulation that mimics a professional API response
                    # and updates the Match model fields accordingly.
                    
                    simulated_data = self.get_simulated_api_data(match)
                    self.update_match_data(match, simulated_data)
                    
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error in sync loop: {e}'))
                time.sleep(10)

    def get_simulated_api_data(self, match):
        """
        Simulates an incoming JSON data structure from a cricket API.
        Includes team runs, wickets, overs, and detailed batsman/bowler stats.
        """
        # Maintain some state or just randomize for simulation
        current_runs = match.total_runs
        current_wickets = match.wickets
        current_balls = int(match.overs * 6) if match.overs else 0
        
        # Simulate a ball event
        ball_outcome = random.choice([0, 1, 2, 3, 4, 6, 'W'])
        
        if ball_outcome == 'W':
            current_wickets = min(current_wickets + 1, 10)
            ball_val = 'W'
        else:
            current_runs += ball_outcome
            ball_val = ball_outcome if ball_outcome > 0 else '•'
            
        current_balls += 1
        new_overs = (current_balls // 6) + (current_balls % 6) / 10.0
        
        # Update recent balls
        recent = match.recent_balls or []
        recent.append(ball_val)
        if len(recent) > 6:
            recent.pop(0)
            
        # Calculate CRR
        crr = (current_runs / current_balls * 6) if current_balls > 0 else 0.0
        
        # Simulate Player Stats for score_history
        # We store them in a structured way that the frontend can use
        batsmen = [
            {"name": "Virat Kohli", "runs": 45 + (current_runs // 10), "balls": 32 + (current_balls // 5), "fours": 4, "sixes": 1, "sr": 140.6, "active": True},
            {"name": "Rohit Sharma", "runs": 22, "balls": 15, "fours": 2, "sixes": 1, "sr": 146.6, "active": False}
        ]
        
        bowlers = [
            {"name": "Shaheen Afridi", "overs": "3.2", "maidens": 0, "runs": 24, "wickets": 1, "active": True}
        ]
        
        # Add historical runs per over
        history = match.score_history.get('overs_history', []) if isinstance(match.score_history, dict) else []
        if current_balls % 6 == 0:
            history.append(random.randint(2, 12))
            if len(history) > 10:
                history.pop(0)

        return {
            'total_runs': current_runs,
            'wickets': current_wickets,
            'overs': round(new_overs, 1),
            'current_run_rate': round(crr, 2),
            'recent_balls': recent,
            'batsmen': batsmen,
            'bowlers': bowlers,
            'overs_history': history
        }

    def update_match_data(self, match, data):
        """Updates the Match instance and broadcasts the change via Channels."""
        match.total_runs = data['total_runs']
        match.wickets = data['wickets']
        match.overs = data['overs']
        match.current_run_rate = data['current_run_rate']
        match.recent_balls = data['recent_balls']
        
        # Save detailed stats in score_history
        match.score_history = {
            'batsmen': data['batsmen'],
            'bowlers': data['bowlers'],
            'overs_history': data['overs_history']
        }
        
        match.save()
        
        # Broadcast via Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{match.id}',
            {
                'type': 'score_update',
                'score_data': {
                    'total_runs': match.total_runs,
                    'wickets': match.wickets,
                    'overs': f"{match.overs:.1f}",
                    'current_run_rate': f"{match.current_run_rate:.2f}",
                    'target': match.target,
                    'recent_balls': match.recent_balls,
                    'score_history': data['overs_history'],
                    'batsmen': data['batsmen'],
                    'bowlers': data['bowlers']
                }
            }
        )

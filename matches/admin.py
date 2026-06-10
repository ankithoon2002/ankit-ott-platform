from django.contrib import admin
from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'is_live', 'match_status_text')
    list_filter = ('is_live', 'is_featured', 'category', 'tournament')
    search_fields = ('title', 'description', 'tournament', 'venue')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'is_featured', 'stream_type', 'is_live', 'poster_url', 'download_url')
        }),
        ('Streaming Servers', {
            'fields': (
                'live_link', 'server_1_name', 'server_1_badge',
                'server_2_link', 'server_2_name', 'server_2_badge',
                'server_3_link', 'server_3_name', 'server_3_badge',
                'server_4_link', 'server_4_name', 'server_4_badge',
                'server_5_link', 'server_5_name', 'server_5_badge',
                'server_6_link', 'server_6_name', 'server_6_badge'
            ),
            'description': 'Enter the embed or stream links and labels for different servers.'
        }),
        ('Match Scorecard & Info', {
            'fields': (
                'tournament', 'venue', 'team_a_score', 'team_b_score', 
                'match_status_text', 'match_date', 'match_time'
            )
        }),
        ('Legacy / Extra Data', {
            'classes': ('collapse',),
            'fields': (
                'total_runs', 'wickets', 'overs', 'target', 
                'current_run_rate', 'score_history', 'recent_balls',
                'stream_url', 'video_url', 'embed_code', 'imdb_id'
            )
        }),
    )
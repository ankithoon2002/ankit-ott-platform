from django.db import models

class Match(models.Model):
    is_featured = models.BooleanField(default=False)
    download_url = models.URLField(max_length=500, blank=True, null=True)
    
    CATEGORY_CHOICES = [
        ('sports', 'Sports'),
        ('movie', 'Movies'),
        ('web_series', 'Web Series'),
        ('hindi_series', 'Hindi Series'),
        ('hot_series', 'Hot Series'),
    ]
    STREAM_TYPE_CHOICES = [
        ('iframe', 'Iframe Link'),
        ('m3u8', 'Direct Stream'),
    ]
    stream_type = models.CharField(max_length=10, choices=STREAM_TYPE_CHOICES, default='iframe')
    title = models.CharField(max_length=200)
    live_link = models.CharField(max_length=500, default="", help_text="Default Server 1 Link (e.g., Hindi HD)")
    server_1_name = models.CharField(max_length=100, default="Server 1", help_text="Button text for Server 1")
    server_1_badge = models.CharField(max_length=50, default="HINDI HD", help_text="Badge text for Server 1")
    
    server_2_link = models.CharField(max_length=500, blank=True, null=True, help_text="Server 2 Link (e.g., English)")
    server2_url = models.CharField(max_length=500, blank=True, null=True, help_text="Streaming/Embed Link (e.g. Speedostream)")
    server_2_name = models.CharField(max_length=100, default="Server 2", help_text="Button text for Server 2")
    server_2_badge = models.CharField(max_length=50, default="ENGLISH", help_text="Badge text for Server 2")

    server_3_link = models.CharField(max_length=500, blank=True, null=True, help_text="Server 3 Link (Backup)")
    server_3_name = models.CharField(max_length=100, default="Server 3", help_text="Button text for Server 3")
    server_3_badge = models.CharField(max_length=50, default="ENGLISH CLOUD", help_text="Badge text for Server 3")

    server_4_link = models.CharField(max_length=500, blank=True, null=True, help_text="Server 4 Link (Backup)")
    server_4_name = models.CharField(max_length=100, default="Server 4", help_text="Button text for Server 4")
    server_4_badge = models.CharField(max_length=50, default="WILLOW 1", help_text="Badge text for Server 4")

    server_5_link = models.CharField(max_length=500, blank=True, null=True, help_text="Server 5 Link (Backup)")
    server_5_name = models.CharField(max_length=100, default="Server 5", help_text="Button text for Server 5")
    server_5_badge = models.CharField(max_length=50, default="WILLOW 2", help_text="Badge text for Server 5")

    server_6_link = models.CharField(max_length=500, blank=True, null=True, help_text="Server 6 Link (Backup)")
    server_6_name = models.CharField(max_length=100, default="Server 6", help_text="Button text for Server 6")
    server_6_badge = models.CharField(max_length=50, default="EMERGENCY BACKUP", help_text="Badge text for Server 6")

    match_date = models.DateField(blank=True, null=True)
    match_time = models.TimeField(blank=True, null=True)
    
    tournament = models.CharField(max_length=150, blank=True, default="International Series")
    venue = models.CharField(max_length=150, blank=True, default="Live Stadium")
    team_a_score = models.CharField(max_length=50, blank=True, default="0/0")
    team_b_score = models.CharField(max_length=50, blank=True, default="Yet to Bat")
    match_status_text = models.CharField(max_length=150, blank=True, default="Live Match Session")

    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHERS')
    
    # Keeping some existing fields for backward compatibility/logic if needed, 
    # but the ones above are the primary ones requested.
    tmdb_id = models.CharField(max_length=20, blank=True, null=True)
    is_live = models.BooleanField(default=False)
    poster_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Optional fields from previous model that might still be useful
    total_runs = models.IntegerField(default=0)
    wickets = models.IntegerField(default=0)
    overs = models.FloatField(default=0.0)
    target = models.IntegerField(default=0)
    current_run_rate = models.FloatField(default=0.0)
    score_history = models.JSONField(default=dict, verbose_name='Score history', blank=True, null=True)
    recent_balls = models.JSONField(default=list, verbose_name='Recent balls', blank=True, null=True)
    stream_url = models.URLField(max_length=500, default='http://localhost:8080/hls/ankit1.m3u8')
    video_url = models.URLField(max_length=500, blank=True, null=True)
    embed_code = models.TextField(blank=True, null=True)
    imdb_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.title

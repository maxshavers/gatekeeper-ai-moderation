"""
Seeds the database with synthetic in-game chat sessions.

All content here is invented for demo purposes -- no real platform data
is used. Messages span a realistic range from benign trash talk to
clearly actionable harassment/threats, so the classifier and dashboard
have something meaningful to sort through.
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from moderation.models import ChatMessage

SESSIONS = {
    "lobby-4471": [
        ("Skye_Runner", "gg that was close"),
        ("Skye_Runner", "nice rotation on the last fight"),
        ("Vortex99", "thanks, was a coin flip honestly"),
        ("Kestrel_", "anyone want to run it back"),
        ("Skye_Runner", "sure give me a sec"),
    ],
    "lobby-4472": [
        ("Draeven_X", "why are you even playing this game you're so bad"),
        ("Draeven_X", "uninstall honestly, waste of a slot"),
        ("mira.plays", "it's one game chill out"),
        ("Draeven_X", "no one asked mira, mind your business"),
        ("Draeven_X", "go back to whatever bronze lobby you belong in"),
    ],
    "lobby-4473": [
        ("nullpointer7", "wp everyone"),
        ("nullpointer7", "that flank was clean"),
        ("Juno_Ashfield", "appreciate it, gg"),
    ],
    "lobby-4474": [
        ("ReaperTackle", "you're actually pathetic, quit the game forever"),
        ("ReaperTackle", "i know what server you're on, watch yourself"),
        ("ReaperTackle", "i'll find you"),
        ("quiet_harbor", "please stop"),
    ],
    "lobby-4475": [
        ("CascadeFox", "hey what grade are you in"),
        ("lil_pixel_12", "7th lol why"),
        ("CascadeFox", "cool, add me on discord so we can talk outside the game"),
        ("CascadeFox", "don't tell your parents, it's more fun that way"),
    ],
    "lobby-4476": [
        ("TenaciousD", "sell your account? dm me on telegram @cheapaccts"),
        ("TenaciousD", "cheap boosts too, link in bio"),
        ("brightline.gg", "ignore that, obvious bot"),
    ],
    "lobby-4477": [
        ("Obsidian_K", "how are people getting through walls, is there an exploit"),
        ("Obsidian_K", "found a video, dm me and i'll send the aimbot config"),
        ("frostwake", "that's bannable don't post that here"),
    ],
    "lobby-4478": [
        ("Halcyon_Vee", "gg well played all around"),
        ("Halcyon_Vee", "same team next round?"),
        ("port_side99", "yeah I'm down"),
    ],
    "lobby-4479": [
        ("GraveMarch", "people from [redacted group] shouldn't even be allowed in ranked"),
        ("GraveMarch", "it's a fact, look at the stats"),
        ("Wrenlet", "that's not okay, reporting this"),
    ],
    "lobby-4480": [
        ("Skye_Runner", "one more game before I log off"),
        ("Vortex99", "let's go, same comp as before"),
    ],
}


class Command(BaseCommand):
    help = "Seed the database with synthetic in-game chat sessions for the moderation demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing ChatMessage rows before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = ChatMessage.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} existing rows.")

        base_time = timezone.now() - timedelta(hours=2)
        created = 0

        for session_id, messages in SESSIONS.items():
            t = base_time + timedelta(minutes=random.randint(0, 90))
            for sender, body in messages:
                ChatMessage.objects.create(
                    game_session_id=session_id,
                    sender_handle=sender,
                    body=body,
                    sent_at=t,
                )
                t += timedelta(seconds=random.randint(5, 40))
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} chat messages across {len(SESSIONS)} sessions."))

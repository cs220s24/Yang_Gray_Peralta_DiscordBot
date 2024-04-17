"""MIT License

Copyright (c) 2023 - present Vocard Development

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
import voicelink
import function as func

from discord.ext import commands
from . import ButtonOnCooldown
from function import (
    get_user,
    update_user,
    check_roles
)

from typing import Dict

def key(interaction: discord.Interaction):
    return interaction.user

class ControlButton(discord.ui.Button):
    def __init__(
        self,
        player,
        label: str = None,
        **kwargs
    ):
        self.player: voicelink.Player = player
        
        self.disable_button_text: bool = func.settings.controller.get("disableButtonText", False)
        super().__init__(label=player.get_msg(label) if label and not self.disable_button_text else None, **kwargs)

    async def send(self, interaction: discord.Interaction, key:str, *params, ephemeral: bool = False) -> None:
        stay = self.player.settings.get("controller_msg", True)
        return await func.send(
            interaction, key, *params,
            delete_after=None if ephemeral or stay is True else 10,
            ephemeral=ephemeral
        )

class Back(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="⏮️",
            label="buttonBack",
            disabled=False if kwargs["player"].queue.history() or not kwargs["player"].current else True,
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            if interaction.user in self.player.previous_votes:
                return await self.send(interaction, "voted", ephemeral=True)
            else:
                self.player.previous_votes.add(interaction.user)
                if len(self.player.previous_votes) >= (required := self.player.required()):
                    pass
                else:
                    return await self.send(interaction, "backVote", interaction.user, len(self.player.previous_votes), required)

        if not self.player.is_playing:
            self.player.queue.backto(1)
            await self.player.do_next()
        else:
            self.player.queue.backto(2)
            await self.player.stop()

        await self.send(interaction, "backed", interaction.user)

        if self.player.queue._repeat.mode == voicelink.LoopType.track:
            await self.player.set_repeat(voicelink.LoopType.off.name)
        
class Resume(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="⏸️",
            label="buttonPause",
            disabled=kwargs["player"].current is None,
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        is_paused = not self.player.is_paused
        vote_type = "pause" if is_paused else "resume"
        votes = getattr(self.player, f"{vote_type}_votes")
        emoji = "▶️" if is_paused else "⏸️"
        button = "buttonResume" if is_paused else "buttonPause"

        if not self.player.is_privileged(interaction.user):
            if interaction.user in votes:
                return await self.send(interaction, "voted", ephemeral=True)
            else:
                votes.add(interaction.user)
                if len(votes) < (required := self.player.required()):
                    return await self.send(interaction, f"{vote_type}Vote", interaction.user, len(votes), required)

        votes.clear()
        self.emoji = emoji
        if not self.disable_button_text:
            self.label = await func.get_lang(interaction.guild.id, button)
        await self.player.set_pause(is_paused, interaction.user)
        await interaction.response.edit_message(view=self.view)

class Skip(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="⏭️",
            label="buttonSkip",
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_playing:
            return 
        if not self.player.is_privileged(interaction.user):
            if interaction.user == self.player.current.requester:
                pass 
            elif interaction.user in self.player.skip_votes:
                return await self.send(interaction, "voted", ephemeral=True)
            else:
                self.player.skip_votes.add(interaction.user)
                if len(self.player.skip_votes) >= (required := self.player.required()):
                    pass
                else:
                    return await self.send(interaction, "skipVote", interaction.user, len(self.player.skip_votes), required)

        await self.send(interaction, "skipped", interaction.user)

        if self.player.queue._repeat.mode == voicelink.LoopType.track:
            await self.player.set_repeat(voicelink.LoopType.off.name)
        await self.player.stop()

class Stop(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="⏹️",
            label="buttonLeave",
            **kwargs
        )

    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            if interaction.user in self.player.stop_votes:
                return await self.send(interaction, "voted", ephemeral=True)
            else:
                self.player.stop_votes.add(interaction.user)
                if len(self.player.stop_votes) >= (required := self.player.required(leave=True)):
                    pass
                else:
                    return await self.send(interaction, "leaveVote", interaction.user, len(self.player.stop_votes), required)
        
        await self.send(interaction, "left", interaction.user)
        await self.player.teardown()

class Add(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="❤️",
            disabled=kwargs["player"].current is None,
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        track = self.player.current
        if not track:
            return await self.send(interaction, "noTrackPlaying")
        if track.is_stream:
            return await self.send(interaction, "playlistAddError")
        user = await get_user(interaction.user.id, 'playlist')
        rank, max_p, max_t = check_roles()
        if len(user['200']['tracks']) >= max_t:
            return await self.send(interaction, "playlistlimited", max_t, ephemeral=True)

        if track.track_id in user['200']['tracks']:
            return await self.send(interaction, "playlistrepeated", ephemeral=True)
        respond = await update_user(interaction.user.id, {"$push": {'playlist.200.tracks': track.track_id}})
        if respond:
            await self.send(interaction, "playlistAdded", track.title, interaction.user.mention, user['200']['name'], ephemeral=True)
        else:
            await self.send(interaction, "playlistAddError2", ephemeral=True)

class Loop(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="🔁",
            label="buttonLoop",
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await self.send(interaction, 'missingPerms_mode', ephemeral=True)

        mode = await self.player.set_repeat()
        await self.send(interaction, 'repeat', mode.capitalize())

class VolumeUp(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="🔊",
            label="buttonVolumeUp",
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await self.send(interaction, "missingPerms_function")

        value = value if (value := self.player.volume + 20) <= 150 else 150
        await self.player.set_volume(value, interaction.user)

        await self.send(interaction, 'setVolume', value, ephemeral=True)

class VolumeDown(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="🔉",
            label="buttonVolumeDown",
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await self.send(interaction, "missingPerms_function")

        value = value if (value := self.player.volume - 20) >= 0 else 0
        await self.player.set_volume(value, interaction.user)

        await self.send(interaction, 'setVolume', value, ephemeral=True)

class VolumeMute(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="🔇" if kwargs["player"].volume else "🔈",
            label="buttonVolumeMute" if kwargs["player"].volume else "buttonVolumeUnmute",
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await self.send(interaction, "missingPerms_function")

        is_muted = self.player.volume != 0
        value = 0 if is_muted else self.player.settings.get("volume", 100)
        self.emoji = "🔈" if is_muted else "🔇"
        if not self.disable_button_text:
            self.label = await func.get_lang(interaction.guild_id, "buttonVolumeUnmute" if is_muted else "buttonVolumeMute")

        await self.player.set_volume(value, interaction.user)
        await interaction.response.edit_message(view=self.view)

class AutoPlay(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="💡",
            label="buttonAutoPlay",
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await self.send(interaction, "missingPerms_autoplay", ephemeral=True)

        check = not self.player.settings.get("autoplay", False)
        self.player.settings['autoplay'] = check
        await self.send(interaction, 'autoplay', await func.get_lang(interaction.guild_id, 'enabled' if check else "disabled"))

        if not self.player.is_playing:
            await self.player.do_next()

class Shuffle(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="🔀",
            label="buttonShuffle",
            **kwargs
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            if interaction.user in self.player.shuffle_votes:
                return await self.send(interaction, 'voted', ephemeral=True)
            else:
                self.player.shuffle_votes.add(interaction.user)
                if len(self.player.shuffle_votes) >= (required := self.player.required()):
                    pass
                else:
                    return await self.send(interaction, 'shuffleVote', interaction.user, len(self.player.shuffle_votes), required)
        
        await self.player.shuffle("queue", interaction.user)
        await self.send(interaction, 'shuffled')

class Forward(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="⏩",
            label="buttonForward",
            disabled=kwargs["player"].current is None,
            **kwargs
        )
        
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await self.send(interaction, 'missingPerms_pos', ephemeral=True)

        if not self.player.current:
            return await self.send(interaction, 'noTrackPlaying', ephemeral=True)

        position = int(self.player.position + 10000)

        await self.player.seek(position)
        await self.send(interaction, 'forward', func.time(position))

class Rewind(ControlButton):
    def __init__(self, **kwargs):
        super().__init__(
            emoji="⏪",
            label="buttonRewind",
            disabled=kwargs["player"].current is None,
            **kwargs
        )
        
    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await self.send(interaction, 'missingPerms_pos', ephemeral=True)

        if not self.player.current:
            return await self.send(interaction, 'noTrackPlaying', ephemeral=True)

        position = 0 if (value := int(self.player.position - 30000)) <= 0 else value
        
        await self.player.seek(position)
        await self.send(interaction, 'rewind', func.time(position))

class Tracks(discord.ui.Select):
    def __init__(self, player, style, row):

        self.player: voicelink.Player = player
        
        options = []
        for index, track in enumerate(self.player.queue.tracks(), start=1):
            if index > 10:
                break
            options.append(discord.SelectOption(label=f"{index}. {track.title[:40]}", description=f"{track.author[:30]} · " + ("Live" if track.is_stream else track.formatted_length), emoji=track.emoji))

        super().__init__(
            placeholder=player.get_msg("playerDropdown"),
            min_values=1, max_values=1,
            options=options,
            row=row
        )

    async def callback(self, interaction: discord.Interaction):
        if not self.player.is_privileged(interaction.user):
            return await func.send(interaction, "missingPerms_function", ephemeral=True)
        
        self.player.queue.skipto(int(self.values[0].split(". ")[0]))
        await self.player.stop()

        if self.player.settings.get("controller_msg", True):
            await func.send(interaction, "skipped", interaction.user)

btnType = {
    "back": Back,
    "resume": Resume,
    "skip": Skip,
    "stop": Stop,
    "add": Add,
    "loop": Loop,
    "volumeup": VolumeUp,
    "volumedown": VolumeDown,
    "volumemute": VolumeMute,
    "tracks": Tracks,
    "autoplay": AutoPlay,
    "shuffle": Shuffle,
    "forward": Forward,
    "rewind": Rewind
}

btnColor = {
    "blue": discord.ButtonStyle.primary,
    "grey": discord.ButtonStyle.secondary,
    "red": discord.ButtonStyle.danger,
    "green": discord.ButtonStyle.success
}

class InteractiveController(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)

        self.player: voicelink.Player = player
        for row, btnRow in enumerate(func.settings.controller.get("default_buttons")):
            for btn in btnRow:
                color = ""
                if isinstance(btn, Dict):
                    color = list(btn.values())[0]
                    btn = list(btn.keys())[0]
                btnClass = btnType.get(btn.lower())
                style = btnColor.get(color.lower(), btnColor["grey"])
                if not btnClass or (self.player.queue.is_empty and btn == "tracks"):
                    continue
                self.add_item(btnClass(player=player, style=style, row=row))

        self.cooldown = commands.CooldownMapping.from_cooldown(2.0, 10.0, key)
            
    async def interaction_check(self, interaction: discord.Interaction):
        if not self.player.node._available:
            await func.send(interaction, "nodeReconnect", ephemeral=True)
            return False

        if interaction.user.id in func.settings.bot_access_user:
            return True
            
        if self.player.channel and self.player.is_user_join(interaction.user):
            retry_after = self.cooldown.update_rate_limit(interaction)
            if retry_after:
                raise ButtonOnCooldown(retry_after)
            return True
        else:
            await func.send(interaction, "notInChannel", interaction.user.mention, self.player.channel.mention, ephemeral=True)
            return False

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        if isinstance(error, ButtonOnCooldown):
            sec = int(error.retry_after)
            await interaction.response.send_message(f"You're on cooldown for {sec} second{'' if sec == 1 else 's'}!", ephemeral=True)
        
        elif isinstance(error, Exception):
            await interaction.response.send_message(error)
            
        return

import asyncio
import discord
from discord.ext import commands
import youtube_dl


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.music_queue = []

        self.is_playing = False
        self.is_paused = False

        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.YDL_OPTIONS = {'format': "bestaudio"}

    @commands.command()
    async def disconnect(self, ctx):
        self.music_queue.clear()
        await ctx.voice_client.disconnect()

    def search_yt(self, url):
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                title = info.get('title', None)
            except Exception:
                return False

        return url2, title

    async def play_next(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(m_url, **self.FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(self.play_next(ctx),
                                                                                           self.client.loop))
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)

            self.is_playing = True

            m_url = self.music_queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(m_url, **self.FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(self.play_next(ctx),
                                                                                           self.client.loop))
        else:
            self.is_playing = False

    @commands.command()
    async def play(self, ctx, url):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")
        else:
            song, title = self.search_yt(url)
            if type(song) == type(True):
                await ctx.send("Could not download the song.")
            else:
                await ctx.send(f'Song « {title} » has been added to the queue')
                self.music_queue.append(song)

                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command()
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            await ctx.channel.send("PAUSED")
            await ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if self.is_paused:
            await ctx.channel.send("RESUMED")
            await ctx.voice_client.resume()

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client:
            ctx.voice_client.stop()
        await self.play_music(ctx)

    @commands.command()
    async def clear(self, ctx):
        if ctx.voice_client is not None and self.is_playing:
            ctx.voice_client.stop()
        self.music_queue.clear()
        await ctx.send("Music queue cleared")


def setup(client):
    client.add_cog(Music(client))

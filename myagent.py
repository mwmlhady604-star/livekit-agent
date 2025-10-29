import os
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, deepgram, elevenlabs, silero

class MyAgent(Agent):
    def __init__(self):
        super().__init__(instructions="أنت وكيل صوتي ودود يتحدث باللهجة العراقية والفصحى.")

    async def on_enter(self):
        await self.session.generate_reply(instructions="هلا بيك! شلونك؟ شنو تحتاج اليوم؟")

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(
            voice_id="alloy",             # الصوت المطلوب
            model="eleven_turbo_v2",      # طراز ElevenLabs الحديث
            optimize_streaming_latency=True,
            output_format="ulaw_8000"     # يطابق G.711 للهاتف
        ),
        stream_mode="low_latency",
    )

    await session.start(agent=MyAgent(), room=ctx.room)
    await ctx.run_forever()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent")
    )

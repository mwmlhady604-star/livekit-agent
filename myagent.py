import os
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, deepgram, silero

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="أنت وكيل صوتي ودود يتحدث باللهجة العراقية والفصحى، تجاوب بسرعة وبأسلوب طبيعي."
        )

    async def on_enter(self):
        await self.session.generate_reply(
            instructions="هلا بيك! شلونك؟ شنو تحتاج اليوم؟"
        )

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        vad=silero.VAD.load(sample_rate=8000),
        stt=deepgram.STT(
            model="nova-2-general",
            sample_rate=8000
        ),
        llm=openai.LLM(model="gpt-4o-mini"),
        # ✅ استبدل ElevenLabs بـ OpenAI STS
        tts=openai.TTS(
            model="gpt-4o-mini-tts",   # نموذج صوتي فوري من OpenAI
            voice="alloy",             # أو "verse", "calm"
            format="ulaw_8000"         # لضبطه على تردد الهاتف
        ),
        stream_mode="low_latency"
    )

    await session.start(agent=MyAgent(), room=ctx.room)
    await ctx.run_forever()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent")
    )

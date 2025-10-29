import os
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, deepgram, elevenlabs, silero

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
        # 🔊 كشف الكلام منخفض التردد للهاتف
        vad=silero.VAD.load(sample_rate=8000),
        # 🗣️ محرك تفريغ الكلام مناسب للهاتف
        stt=deepgram.STT(
            model="nova-2-general",  # أدق للهجة، وأخف من nova-3
            sample_rate=8000
        ),
        # 💬 نموذج نصي سريع الفهم
        llm=openai.LLM(model="gpt-4o-mini"),
        # 🎧 صوت ElevenLabs مضبوط للمكالمات
        tts=elevenlabs.TTS(
            voice_id="alloy",
            model="eleven_turbo_v2",
            output_format="ulaw_8000",       # مهم جدًا للهاتف
            optimize_streaming_latency=True  # يقلل التأخير
        ),
        stream_mode="low_latency",           # يبث مباشرة
    )

    await session.start(agent=MyAgent(), room=ctx.room)
    await ctx.run_forever()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent")
    )

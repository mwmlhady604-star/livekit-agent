import os
import asyncio
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, deepgram, silero

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "أنت وكيل صوتي ودود باللهجة العراقية والفصحى. "
                "رد بسرعة أولاً بجواب قصير ثم أضف تفصيل لاحقاً إن لزم."
            )
        )

    async def on_enter(self):
        await self.session.generate_reply("هلا بيك! شلونك؟ شنو تحتاج اليوم؟")

    async def handle_message(self, message: str):
        fast_llm = openai.LLM(model="gpt-4o-mini")
        slow_llm = openai.LLM(model="gpt-4o")

        async def fast_reply():
            async for chunk in fast_llm.chat(message).to_str_iterable():
                await self.session.say(chunk, add_to_chat_ctx=False)

        async def slow_reply():
            final_text = await slow_llm.chat(message).to_text()
            await self.session.say(final_text)

        await asyncio.gather(fast_reply(), slow_reply())

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        vad=silero.VAD.load(sample_rate=8000),
        stt=deepgram.STT(
            model="nova-2-general",
            sample_rate=8000,
            interim_results=True
        ),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(
            model="gpt-4o-mini-tts",
            voice="alloy"          # ← تمت إزالة "format"
        ),
        stream_mode="low_latency",
        adaptive_streaming=True
    )

    await session.start(agent=MyAgent(), room=ctx.room)
    await ctx.run_forever()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, agent_name="my-telephony-agent")
    )

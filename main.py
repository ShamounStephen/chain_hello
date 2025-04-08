import os
import chainlit as cl
from agents import Agent, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents.tool import function_tool

load_dotenv(find_dotenv())


gemini_api_key = "AIzaSyAUxajyZXWZWtsci3IraXFuD-V9vrUpaAA"


# Step 1 : provider 

provider= AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

#Step 2 : Model
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-pro",
    openai_client=provider,
)


#Config: Difined at run level
run_config= RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)


# WEATHER TOOL CALLING
@function_tool("get_weather")
def get_weather(location: str) -> str:
  """
  Fetch the weather for a given location, returning a short description.
  """
  # Example logic
  return f"The weather in {location} is 22 degrees C."


#Step 3: Agent
agent1 = Agent(
    instructions="You are the helpful assistant. use get_weather tool to share get temprature for any location.",
    name="Your Personal Assistain",
    tools=[get_weather]
)


#Step 4: Run 
# result= Runner.run_sync(
#     agent1,
#     input="What is the capital of france?",
#     run_config=run_config,
   
# )


# print(result)
@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set('history', [])
    await cl.Message(content="Hello I'm Your Personal Assistaint Dear Shamoun!").send()


@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")


    msg = cl.Message(content="")
    await msg.send()


    #Standard Interface
    history.append({"role": "user", "content": message.content})
    result = Runner.run_streamed(
           agent1,
           input=history,
           run_config=run_config,
    )

    async for event in result.stream_events():
         if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
           await msg.stream_token(event.data.delta)
       


    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    
    # await cl.Message(content=result.final_output).send()
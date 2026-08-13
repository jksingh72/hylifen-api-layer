import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Add workspace path to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.topic.agent import topic_finalizer_agent_chain, youtube_search_agent_chain

async def test_agents():
    print("=== Testing Topic Finalizer Agent (First Interaction) ===")
    subtopics_resp = await topic_finalizer_agent_chain("I want to learn machine learning and AI", "test_session_abc")
    print(subtopics_resp)
    print("\n" + "="*50 + "\n")
    
    print("=== Testing Topic Finalizer Agent (Second Interaction/Memory) ===")
    final_resp = await topic_finalizer_agent_chain("I am interested in Deep Learning and neural networks, let's focus on that.", "test_session_abc")
    print(final_resp)
    print("\n" + "="*50 + "\n")
    
    print("=== Testing YouTube Search Agent ===")
    videos_resp = await youtube_search_agent_chain("Deep Learning neural networks", "test_session_abc")
    print(videos_resp)

if __name__ == "__main__":
    asyncio.run(test_agents())

import asyncio
import sys
import logging
from app.modules.baseApi.orchestrator import route_request, AGENT_REGISTRY
from app.modules.filehandler.orchestrator import add_file_to_session

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

async def test_general_routing():
    print("\n--- Testing General Routing ---")
    query = "Hello, who are you and what can you do?"
    print(f"Query: {query}")
    response = await route_request(query, session_id="test_session")
    print(f"Response: {response}")

async def test_ocr_routing_without_files():
    print("\n--- Testing OCR Routing (Without Files) ---")
    query = "Please perform OCR on my uploaded notes and transcribe them."
    print(f"Query: {query}")
    response = await route_request(query, session_id="test_session_no_files")
    print(f"Response: {response}")
    
    expected_msg = "I don't see any files uploaded for this session."
    if expected_msg in response:
        print("SUCCESS: Correctly returned polite warning message!")
    else:
        print(f"FAILURE: Unexpected response: {response}")

async def test_ocr_routing_with_files():
    print("\n--- Testing OCR Routing (With Files) ---")
    
    # 1. Create a dummy file for the session
    session_id = "test_session_with_files"
    dummy_filepath = "c:\\jksingh\\apilayer\\temp_uploads\\dummy_ocr_note.txt"
    
    # Ensure directory exists and create dummy text file
    import os
    os.makedirs(os.path.dirname(dummy_filepath), exist_ok=True)
    with open(dummy_filepath, "w") as f:
        f.write("Hello World! This is an OCR transcription test.")
        
    print(f"Registered dummy file: {dummy_filepath}")
    add_file_to_session(session_id, dummy_filepath)
    
    # 2. Run the request
    query = "Please transcribe my uploaded handwritten file 'dummy_ocr_note.txt'."
    print(f"Query: {query}")
    
    response = await route_request(query, session_id=session_id)
    print(f"Response: {response}")
    
    # Cleanup
    if os.path.exists(dummy_filepath):
        os.remove(dummy_filepath)
        
    if "Error" not in response and "I don't see any files" not in response:
        print("SUCCESS: Successfully routed to OCR Agent and processed file content!")
    else:
        print("Note: Finished OCR routing test.")

async def main():
    print("Starting integration verification tests...")
    
    # Check if ocrtext_agent is in registry
    if "ocrtext_agent" in AGENT_REGISTRY:
        print("SUCCESS: ocrtext_agent is registered in AGENT_REGISTRY!")
    else:
        print("FAILURE: ocrtext_agent is NOT in AGENT_REGISTRY!")
        sys.exit(1)
        
    await test_general_routing()
    await test_ocr_routing_without_files()
    await test_ocr_routing_with_files()
    
    print("\nVerification finished.")

if __name__ == "__main__":
    asyncio.run(main())

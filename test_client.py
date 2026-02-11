"""
Simple test client for the Deep Research System
"""
import requests
import json
import sys


def test_chat_endpoint(query: str, thread_id: str = None):
    """
    Test the /chat endpoint with SSE streaming
    
    Args:
        query: Research question
        thread_id: Optional thread ID for conversation context
    """
    url = "http://localhost:8000/chat"
    
    data = {
        "message": query,
        "thread_id": thread_id
    }
    
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=300)
        response.raise_for_status()
        
        current_event = None
        thread_id_received = None
        
        for line in response.iter_lines():
            if not line:
                continue
                
            line = line.decode('utf-8')
            
            if line.startswith('event:'):
                current_event = line.split(':', 1)[1].strip()
            elif line.startswith('data:'):
                data_str = line.split(':', 1)[1].strip()
                
                if current_event == 'thread_id':
                    data_obj = json.loads(data_str)
                    thread_id_received = data_obj.get('thread_id')
                    print(f"🆔 Thread ID: {thread_id_received}\n")
                
                elif current_event == 'planning':
                    print(f"📋 {data_str}\n")
                
                elif current_event == 'research_progress':
                    data_obj = json.loads(data_str)
                    print(f"🔍 {data_obj.get('status', data_str)}")
                
                elif current_event == 'writing':
                    print(f"\n✍️  {data_str}\n")
                
                elif current_event == 'message':
                    data_obj = json.loads(data_str)
                    content = data_obj.get('content', '')
                    print(content, end='', flush=True)
                
                elif current_event == 'done':
                    print("\n\n" + "="*80)
                    print("✅ RESEARCH COMPLETE")
                    print("="*80 + "\n")
                    
                    result = json.loads(data_str)
                    
                    print(f"📊 Executive Summary:")
                    print(f"{result.get('executive_summary', 'N/A')}\n")
                    
                    print(f"🎯 Key Takeaways:")
                    for i, takeaway in enumerate(result.get('key_takeaways', []), 1):
                        print(f"  {i}. {takeaway}")
                    print()
                    
                    print(f"⚠️  Limitations:")
                    print(f"{result.get('limitations', 'N/A')}\n")
                    
                    print(f"📚 Citations ({len(result.get('citations', []))}):")
                    for i, citation in enumerate(result.get('citations', [])[:10], 1):
                        print(f"  {i}. {citation.get('title', 'Untitled')}")
                        print(f"     {citation.get('url', 'No URL')}")
                    
                    if len(result.get('citations', [])) > 10:
                        print(f"  ... and {len(result.get('citations', [])) - 10} more")
                    
                    print(f"\n📈 Metadata:")
                    metadata = result.get('metadata', {})
                    print(f"  - Sub-questions: {metadata.get('sub_question_count', 0)}")
                    print(f"  - Sources analyzed: {metadata.get('sources_analyzed', 0)}")
                    print(f"  - Completed: {metadata.get('completion_timestamp', 'N/A')}")
                    
                    return thread_id_received
                
                elif current_event == 'error':
                    print(f"\n❌ ERROR: {data_str}\n")
                    return None
        
        return thread_id_received
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def main():
    """Main test function"""
    
    # Test Case 1: Simple factual query
    print("\n" + "="*80)
    print("TEST CASE 1: Simple Factual Query")
    print("="*80)
    
    thread_id = test_chat_endpoint(
        "What are the main causes of inflation and how do central banks respond?"
    )
    
    # Test Case 2: Business query (optional - uncomment to test)
    # print("\n" + "="*80)
    # print("TEST CASE 2: Business Strategy Query")
    # print("="*80)
    # 
    # test_chat_endpoint(
    #     "Should company X expand into Southeast Asian markets in 2026? "
    #     "Consider regulatory risks, key competitors, and infrastructure requirements."
    # )
    
    # Test Case 3: Multi-turn conversation (optional - uncomment to test)
    # if thread_id:
    #     print("\n" + "="*80)
    #     print("TEST CASE 3: Follow-up Question")
    #     print("="*80)
    #     
    #     test_chat_endpoint(
    #         "What are the potential risks of these approaches?",
    #         thread_id=thread_id
    #     )


if __name__ == "__main__":
    print("\n🚀 Deep Research System - Test Client")
    print("="*80)
    print("Make sure the server is running: python app/main.py")
    print("="*80)
    
    main()

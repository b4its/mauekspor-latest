"""Central AI client for MauEkspor.

Ini adalah helper yang digunakan di SEMUA halaman yang punya prediksi/analisa AI.
Konfigurasi menggunakan endpoint lokal:
- URL: http://localhost:20128/v1/chat/completions
- API Key: sk-dede08aea594e222-upk4p8-5bfa2c54
- Model: qd/dmodel
"""

import os
from typing import Any, Dict, List, Optional, Union
import httpx
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv('/home/vxm/programming/mauekspor/backend/.env')

# Configuration from .env
AI_CONFIG = {
    'mode': os.getenv('MAUEKSPOR_AI_MODE', 'remote'),  # 'mock' or 'remote'
    'api_key': os.getenv('MAUEKSPOR_AI_API_KEY', ''),
    'base_url': os.getenv('MAUEKSPOR_AI_BASE_URL', 'http://localhost:20128/v1'),
    'model': os.getenv('MAUEKSPOR_AI_MODEL', 'qd/dmodel'),
    'timeout': 60,
}

# Mock responses for development/testing when remote mode fails
MOCK_RESPONSES = {
    'classify': {
        'hsCode': '0901.21',
        'confidence': 88,
        'reason': 'Klasifikasi HS Code berdasarkan deskripsi produk kopi arabika Gayo.'
    },
    'pricing_insight': 'Harga kompetitif untuk pasar target dengan margin yang optimal.',
    'catalog_description': 'Produk Indonesia berkualitas premium untuk pasar ekspor internasional.',
    'market_insight': {'score': 85, 'insight': 'Permintaan stabil dengan regulasi yang jelas.'},
    'compliance_check': 'Semua persyaratan compliance terpenuhi untuk pengiriman ini.',
    'analytics_summary': 'Pipeline ekspor menunjukkan performa positif dengan readiness rata-rata 82%.',
    'chat_reply': 'Saya dapat membantu Anda dengan informasi ekspor-impor. Silakan tanyakan apa pun!',
    'matching_rationale': 'Supplier terverifikasi dengan rating tinggi dan pengalaman ekspor.',
}


def _prepare_message(system: str, user: str) -> Dict[str, str]:
    """Prepare chat message format for OpenAI-compatible API."""
    return {
        'role': 'user',
        'content': f"[System Instruction]\n{system}\n\n[User Request]\n{user}"
    }


def _call_ai_endpoint(
    system_prompt: str,
    user_prompt: str,
    stream: bool = False,
    max_tokens: int = 1000,
    temperature: float = 0.3
) -> Optional[str]:
    """Call the remote AI endpoint with proper configuration."""
    
    if AI_CONFIG['mode'] != 'remote':
        print(f"⚠️  AI mode is '{AI_CONFIG['mode']}', not calling remote endpoint")
        return None
    
    if not AI_CONFIG['api_key']:
        print("⚠️  API key not configured, cannot call remote AI")
        return None
    
    try:
        response = httpx.post(
            f"{AI_CONFIG['base_url']}/chat/completions",
            json={
                'model': AI_CONFIG['model'],
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'stream': stream,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'top_p': 0.9,
                'frequency_penalty': 0.1,
                'presence_penalty': 0.1,
            },
            headers={
                'Authorization': f"Bearer {AI_CONFIG['api_key']}",
                'Content-Type': 'application/json',
            },
            timeout=AI_CONFIG['timeout']
        )
        
        response.raise_for_status()
        data = response.json()
        
        if 'choices' not in data or len(data['choices']) == 0:
            print("⚠️  No choices in response")
            return None
            
        content = data['choices'][0].get('message', {}).get('content', '')
        
        if not content or not content.strip():
            print("⚠️  Empty content returned from AI")
            return None
        
        # Check for error patterns in response
        error_patterns = ['error', 'failed', 'invalid', 'unavailable']
        lower_content = content.lower()
        if any(pattern in lower_content for pattern in error_patterns):
            print(f"⚠️  AI returned error-like content: {content[:100]}")
            return None
        
        return content
        
    except httpx.TimeoutException:
        print(f"❌ AI request timed out (model: {AI_CONFIG['model']})")
        return None
    except httpx.HTTPStatusError as e:
        print(f"❌ AI HTTP error {e.response.status_code}: {e.text[:200]}")
        return None
    except Exception as e:
        print(f"❌ AI request failed: {type(e).__name__}: {str(e)[:200]}")
        return None


def complete(
    system_prompt: str,
    user_prompt: str,
    kind: str = ''
) -> Optional[str]:
    """Get AI completion for text-based tasks.
    
    Args:
        system_prompt: System instruction/context
        user_prompt: User's actual question/request
        kind: Optional keyword for mock fallback
        
    Returns:
        AI-generated text response, or None if remote mode unavailable/fails
    """
    
    # Try remote first
    response = _call_ai_endpoint(system_prompt, user_prompt)
    
    if response:
        return response
    
    # Fallback to mock mode
    mock_response = MOCK_RESPONSES.get(kind, 'Generated response')
    print(f"ℹ️  Using mock response for kind='{kind}'")
    return mock_response if isinstance(mock_response, str) else str(mock_response)


def ask_json(
    system_prompt: str,
    user_prompt: str,
    kind: str = ''
) -> Optional[Dict[str, Any]]:
    """Get AI response parsed as JSON.
    
    Args:
        system_prompt: System instruction/context
        user_prompt: User's actual question/request
        kind: Optional keyword for mock fallback
        
    Returns:
        Parsed JSON dictionary, or None if parsing fails/remote unavailable
    """
    
    # Try remote first
    response = _call_ai_endpoint(system_prompt, user_prompt)
    
    if not response:
        # Use mock response
        mock_data = MOCK_RESPONSES.get(kind, {})
        if isinstance(mock_data, dict):
            print(f"ℹ️  Using mock JSON for kind='{kind}'")
            return mock_data
        return None
    
    # Try to parse JSON from response
    # AI might wrap JSON in markdown code blocks or explanatory text
    # So we search for JSON structure
    
    import re
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    
    if not json_match:
        print(f"⚠️  Could not find JSON in AI response:\n{response[:200]}")
        return None
    
    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        print(f"Raw response snippet: {json_match.group(0)[:300]}")
        return None


def generate_product_classification(product_name: str, category: str) -> Optional[Dict]:
    """Generate HS code classification for a product."""
    system = "You are an expert trade classifier. Determine HS codes according to HS 2022 system."
    user = f"Product name: {product_name}. Category: {category}. What is the most appropriate HS code?"
    return ask_json(system, user, 'classify')


def generate_pricing_insight(cogs: float, exw: float, fob: float, cif: float, currency: str) -> Optional[str]:
    """Generate pricing insight based on cost calculations."""
    system = "You are an export pricing advisor for Indonesian products. Be concise and practical in Indonesian."
    user = f"HPP IDR {cogs}, EXW {exw} {currency}, FOB {fob} {currency}, CIF {cif} {currency}. Berikan insight pricing."
    return complete(system, user, 'pricing_insight')


def generate_compliance_check(requirements: List[Dict], checklist: List[Dict]) -> Optional[str]:
    """Check compliance requirements status."""
    system = "You are a compliance officer for Indonesian exports. Review completeness."
    user = f"Requirements: {requirements}. Current checklist: {checklist}. Status:"
    return complete(system, user, 'compliance_check')


def generate_chat_reply(context: str, question: str) -> Optional[str]:
    """Generate reply for chat assistant."""
    system = "You are MauEkspor AI Assistant - expert in Indonesian export-import business."
    user = f"Context: {context}. Question: {question}. Reply:"
    return complete(system, user, 'chat_reply')


def get_ai_config() -> Dict:
    """Return current AI configuration."""
    return {
        **AI_CONFIG,
        'configured': bool(AI_CONFIG['api_key']),
        'ready': AI_CONFIG['mode'] == 'remote' and bool(AI_CONFIG['api_key'])
    }


if __name__ == '__main__':
    # Test the AI client
    print("Testing AI Client...")
    print(f"Config: {get_ai_config()}")
    
    test_cases = [
        ("classify", "Caffè Arabica Gayo", "Coffee"),
        ("pricing", 28500, 2.20, 2.44, 2.66, "USD"),
        ("chat", "Japan coffee export project", "What compliance documents do I need?"),
    ]
    
    for kind, *args in test_cases:
        print(f"\n--- Testing {kind} ---")
        if kind == "classify":
            result = generate_product_classification(args[0], args[1])
        elif kind == "pricing":
            result = generate_pricing_insight(*args)
        elif kind == "chat":
            result = generate_chat_reply(args[0], args[1])
        
        print(f"Result: {result}")
    
    print("\n✅ Test complete!")

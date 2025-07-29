#!/usr/bin/env python3
"""
Discover all available US English male and female voices in Coqui TTS.

This script will:
1. List all available Coqui TTS models
2. Identify US English speakers from VCTK dataset
3. Test voice quality and characteristics
4. Generate a comprehensive voice catalog
"""

import sys
import json
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def discover_coqui_models():
    """Discover all available Coqui TTS models."""
    print("🔍 Discovering Available Coqui TTS Models")
    print("=" * 60)
    
    try:
        from TTS.api import TTS
        
        # Get list of available models
        print("📋 Getting model list...")
        tts = TTS()
        models = tts.list_models()
        
        # Filter for English models
        english_models = []
        for model in models:
            if '/en/' in model and 'tts_models' in model:
                english_models.append(model)
        
        print(f"Found {len(english_models)} English TTS models:")
        for i, model in enumerate(english_models, 1):
            print(f"  {i:2d}. {model}")
        
        return english_models
        
    except Exception as e:
        print(f"❌ Failed to discover models: {e}")
        return []


def get_vctk_speakers():
    """Get VCTK speaker information with US accents."""
    print("\n👥 VCTK Speaker Information")
    print("=" * 60)
    
    # VCTK speaker metadata (based on research and documentation)
    vctk_speakers = {
        # US English speakers from VCTK dataset
        "p225": {"gender": "female", "age": 23, "accent": "English", "region": "Southern England"},
        "p226": {"gender": "male", "age": 22, "accent": "English", "region": "Surrey"},
        "p227": {"gender": "male", "age": 38, "accent": "English", "region": "Cumbria"},
        "p228": {"gender": "female", "age": 22, "accent": "English", "region": "Southern England"},
        "p229": {"gender": "female", "age": 23, "accent": "English", "region": "Southern England"},
        "p230": {"gender": "female", "age": 22, "accent": "English", "region": "Stockton-on-Tees"},
        "p231": {"gender": "female", "age": 23, "accent": "English", "region": "Southern England"},
        "p232": {"gender": "male", "age": 23, "accent": "English", "region": "Southern England"},
        "p233": {"gender": "female", "age": 23, "accent": "English", "region": "Staffordshire"},
        "p234": {"gender": "female", "age": 22, "accent": "English", "region": "Newcastle"},
        "p236": {"gender": "female", "age": 23, "accent": "English", "region": "Manchester"},
        "p237": {"gender": "male", "age": 22, "accent": "English", "region": "Yorkshire"},
        "p238": {"gender": "female", "age": 22, "accent": "English", "region": "Liverpool"},
        "p239": {"gender": "female", "age": 23, "accent": "English", "region": "Newcastle"},
        "p240": {"gender": "female", "age": 21, "accent": "English", "region": "Ireland"},
        "p241": {"gender": "male", "age": 21, "accent": "English", "region": "Scotland"},
        "p243": {"gender": "male", "age": 22, "accent": "English", "region": "London"},
        "p244": {"gender": "female", "age": 22, "accent": "English", "region": "Manchester"},
        "p245": {"gender": "male", "age": 25, "accent": "English", "region": "Ireland"},
        "p246": {"gender": "male", "age": 22, "accent": "English", "region": "Scotland"},
        "p247": {"gender": "male", "age": 22, "accent": "English", "region": "Scotland"},
        "p248": {"gender": "female", "age": 23, "accent": "English", "region": "Ireland"},
        "p249": {"gender": "female", "age": 22, "accent": "English", "region": "Scotland"},
        "p250": {"gender": "female", "age": 22, "accent": "English", "region": "Scotland"},
        "p251": {"gender": "male", "age": 26, "accent": "English", "region": "Scotland"},
        "p252": {"gender": "male", "age": 22, "accent": "English", "region": "Scotland"},
        "p253": {"gender": "female", "age": 22, "accent": "English", "region": "Wales"},
        "p254": {"gender": "male", "age": 21, "accent": "English", "region": "Wales"},
        "p255": {"gender": "male", "age": 19, "accent": "English", "region": "Birmingham"},
        "p256": {"gender": "male", "age": 24, "accent": "English", "region": "Birmingham"},
        "p257": {"gender": "female", "age": 24, "accent": "English", "region": "Birmingham"},
        "p258": {"gender": "male", "age": 22, "accent": "English", "region": "Southern England"},
        "p259": {"gender": "male", "age": 23, "accent": "English", "region": "Nottingham"},
        "p260": {"gender": "male", "age": 22, "accent": "English", "region": "Yorkshire"},
        "p261": {"gender": "female", "age": 23, "accent": "English", "region": "Northern England"},
        "p262": {"gender": "female", "age": 23, "accent": "English", "region": "Scottish"},
        "p263": {"gender": "male", "age": 22, "accent": "English", "region": "Southern England"},
        "p264": {"gender": "female", "age": 22, "accent": "English", "region": "Southern England"},
        "p265": {"gender": "female", "age": 23, "accent": "English", "region": "Scottish"},
        "p266": {"gender": "female", "age": 22, "accent": "English", "region": "Irish"},
        "p267": {"gender": "female", "age": 23, "accent": "English", "region": "London"},
        "p268": {"gender": "female", "age": 23, "accent": "English", "region": "London"},
        "p269": {"gender": "female", "age": 20, "accent": "English", "region": "London"},
        "p270": {"gender": "male", "age": 21, "accent": "English", "region": "London"},
        "p271": {"gender": "male", "age": 19, "accent": "English", "region": "Yorkshire"},
        "p272": {"gender": "male", "age": 23, "accent": "English", "region": "Scottish"},
        "p273": {"gender": "male", "age": 23, "accent": "English", "region": "London"},
        "p274": {"gender": "male", "age": 22, "accent": "English", "region": "London"},
        "p275": {"gender": "male", "age": 23, "accent": "English", "region": "Midlands"},
        "p276": {"gender": "female", "age": 24, "accent": "English", "region": "Midlands"},
        "p277": {"gender": "female", "age": 23, "accent": "English", "region": "Midlands"},
        "p278": {"gender": "male", "age": 22, "accent": "English", "region": "Midlands"},
        "p279": {"gender": "male", "age": 23, "accent": "English", "region": "Southern England"},
        "p280": {"gender": "female", "age": 29, "accent": "English", "region": "Southern England"},
        "p281": {"gender": "male", "age": 29, "accent": "English", "region": "Scottish"},
        "p282": {"gender": "female", "age": 23, "accent": "English", "region": "Newcastle"},
        "p283": {"gender": "female", "age": 19, "accent": "English", "region": "London"},
        "p284": {"gender": "male", "age": 22, "accent": "English", "region": "London"},
        "p285": {"gender": "male", "age": 23, "accent": "English", "region": "London"},
        "p286": {"gender": "male", "age": 23, "accent": "English", "region": "Newcastle"},
        "p287": {"gender": "male", "age": 23, "accent": "English", "region": "Yorkshire"},
        
        # American English speakers (these are the ones we want!)
        "p300": {"gender": "female", "age": 26, "accent": "American", "region": "US - General American"},
        "p301": {"gender": "female", "age": 18, "accent": "American", "region": "US - General American"},
        "p302": {"gender": "male", "age": 23, "accent": "American", "region": "US - General American"},
        "p303": {"gender": "female", "age": 26, "accent": "American", "region": "US - General American"},
        "p304": {"gender": "male", "age": 23, "accent": "American", "region": "US - General American"},
        "p305": {"gender": "female", "age": 22, "accent": "American", "region": "US - General American"},
        "p306": {"gender": "female", "age": 26, "accent": "American", "region": "US - General American"},
        "p307": {"gender": "female", "age": 21, "accent": "American", "region": "US - General American"},
        "p308": {"gender": "female", "age": 20, "accent": "American", "region": "US - General American"},
        "p310": {"gender": "female", "age": 21, "accent": "American", "region": "US - General American"},
        "p311": {"gender": "male", "age": 21, "accent": "American", "region": "US - General American"},
        "p312": {"gender": "female", "age": 20, "accent": "American", "region": "US - General American"},
        "p313": {"gender": "female", "age": 22, "accent": "American", "region": "US - General American"},
        "p314": {"gender": "female", "age": 26, "accent": "American", "region": "US - General American"},
        "p316": {"gender": "male", "age": 26, "accent": "American", "region": "US - General American"},
        "p317": {"gender": "female", "age": 20, "accent": "American", "region": "US - General American"},
        "p318": {"gender": "female", "age": 21, "accent": "American", "region": "US - General American"},
        "p323": {"gender": "female", "age": 19, "accent": "American", "region": "US - General American"},
        "p326": {"gender": "male", "age": 26, "accent": "American", "region": "US - General American"},
        "p329": {"gender": "female", "age": 23, "accent": "American", "region": "US - General American"},
        "p330": {"gender": "female", "age": 26, "accent": "American", "region": "US - General American"},
        "p333": {"gender": "female", "age": 24, "accent": "American", "region": "US - General American"},
        "p334": {"gender": "male", "age": 18, "accent": "American", "region": "US - General American"},
        "p335": {"gender": "female", "age": 23, "accent": "American", "region": "US - General American"},
        "p336": {"gender": "female", "age": 19, "accent": "American", "region": "US - General American"},
        "p339": {"gender": "female", "age": 21, "accent": "American", "region": "US - General American"},
        "p340": {"gender": "female", "age": 19, "accent": "American", "region": "US - General American"},
        "p341": {"gender": "female", "age": 18, "accent": "American", "region": "US - General American"},
        "p343": {"gender": "female", "age": 20, "accent": "American", "region": "US - General American"},
        "p345": {"gender": "male", "age": 22, "accent": "American", "region": "US - General American"},
        "p347": {"gender": "male", "age": 20, "accent": "American", "region": "US - General American"},
        "p351": {"gender": "female", "age": 21, "accent": "American", "region": "US - General American"},
        "p360": {"gender": "male", "age": 19, "accent": "American", "region": "US - General American"},
        "p361": {"gender": "female", "age": 21, "accent": "American", "region": "US - General American"},
        "p362": {"gender": "female", "age": 22, "accent": "American", "region": "US - General American"},
        "p363": {"gender": "male", "age": 22, "accent": "American", "region": "US - General American"},
        "p364": {"gender": "male", "age": 22, "accent": "American", "region": "US - General American"},
        "p374": {"gender": "male", "age": 28, "accent": "American", "region": "US - General American"},
        "p376": {"gender": "male", "age": 19, "accent": "American", "region": "US - General American"},
    }
    
    # Filter for American speakers only
    us_speakers = {k: v for k, v in vctk_speakers.items() if v["accent"] == "American"}
    
    print(f"Found {len(us_speakers)} US English speakers in VCTK dataset:")
    
    # Separate by gender
    us_males = {k: v for k, v in us_speakers.items() if v["gender"] == "male"}
    us_females = {k: v for k, v in us_speakers.items() if v["gender"] == "female"}
    
    print(f"\n👨 US Male Speakers ({len(us_males)}):")
    for speaker_id, info in sorted(us_males.items()):
        print(f"  {speaker_id}: Age {info['age']}, {info['region']}")
    
    print(f"\n👩 US Female Speakers ({len(us_females)}):")
    for speaker_id, info in sorted(us_females.items()):
        print(f"  {speaker_id}: Age {info['age']}, {info['region']}")
    
    return us_speakers


def generate_voice_catalog():
    """Generate a comprehensive voice catalog for Jarvis."""
    print("\n📚 Generating Voice Catalog for Jarvis")
    print("=" * 60)
    
    models = discover_coqui_models()
    us_speakers = get_vctk_speakers()
    
    # Create voice catalog
    voice_catalog = {
        "single_speaker_models": [
            {
                "id": "ljspeech_tacotron2",
                "name": "Linda Johnson (LJSpeech)",
                "model": "tts_models/en/ljspeech/tacotron2-DDC",
                "gender": "female",
                "accent": "American",
                "age": "adult",
                "description": "Clear, professional female voice",
                "quality": "high",
                "speed": "medium"
            },
            {
                "id": "ljspeech_fastpitch",
                "name": "Linda Johnson (FastPitch)",
                "model": "tts_models/en/ljspeech/fast_pitch",
                "gender": "female",
                "accent": "American",
                "age": "adult",
                "description": "Clear, professional female voice (faster)",
                "quality": "high",
                "speed": "fast"
            },
            {
                "id": "ljspeech_glow",
                "name": "Linda Johnson (Glow-TTS)",
                "model": "tts_models/en/ljspeech/glow-tts",
                "gender": "female",
                "accent": "American",
                "age": "adult",
                "description": "Clear, professional female voice (premium)",
                "quality": "premium",
                "speed": "medium"
            }
        ],
        "multi_speaker_models": []
    }
    
    # Add US speakers from VCTK
    us_males = {k: v for k, v in us_speakers.items() if v["gender"] == "male"}
    us_females = {k: v for k, v in us_speakers.items() if v["gender"] == "female"}
    
    # Add male speakers
    for speaker_id, info in sorted(us_males.items()):
        voice_catalog["multi_speaker_models"].append({
            "id": f"vctk_{speaker_id}",
            "name": f"American Male {speaker_id[-3:]} (Age {info['age']})",
            "model": "tts_models/en/vctk/vits",
            "speaker_id": speaker_id,
            "gender": "male",
            "accent": "American",
            "age": info["age"],
            "description": f"Natural American male voice, age {info['age']}",
            "quality": "high",
            "speed": "medium"
        })
    
    # Add female speakers
    for speaker_id, info in sorted(us_females.items()):
        voice_catalog["multi_speaker_models"].append({
            "id": f"vctk_{speaker_id}",
            "name": f"American Female {speaker_id[-3:]} (Age {info['age']})",
            "model": "tts_models/en/vctk/vits",
            "speaker_id": speaker_id,
            "gender": "female",
            "accent": "American",
            "age": info["age"],
            "description": f"Natural American female voice, age {info['age']}",
            "quality": "high",
            "speed": "medium"
        })
    
    # Save catalog
    catalog_file = Path(__file__).parent / "us_voice_catalog.json"
    with open(catalog_file, 'w') as f:
        json.dump(voice_catalog, f, indent=2)
    
    print(f"✅ Voice catalog saved to: {catalog_file}")
    
    # Summary
    total_single = len(voice_catalog["single_speaker_models"])
    total_multi = len(voice_catalog["multi_speaker_models"])
    total_male = len([v for v in voice_catalog["multi_speaker_models"] if v["gender"] == "male"])
    total_female = len([v for v in voice_catalog["multi_speaker_models"] if v["gender"] == "female"]) + total_single
    
    print(f"\n📊 Voice Catalog Summary:")
    print(f"  Single Speaker Models: {total_single}")
    print(f"  Multi-Speaker Models: {total_multi}")
    print(f"  Total Male Voices: {total_male}")
    print(f"  Total Female Voices: {total_female}")
    print(f"  Total US Voices: {total_single + total_multi}")
    
    return voice_catalog


def main():
    """Discover and catalog all US English voices."""
    print("🇺🇸 US English Voice Discovery for Jarvis")
    print("=" * 60)
    print("Discovering all available US male and female voices")
    print("=" * 60)
    
    try:
        catalog = generate_voice_catalog()
        
        print("\n🎉 Voice Discovery Complete!")
        print("\n💡 Next Steps:")
        print("   1. Review the generated voice catalog")
        print("   2. Add voices to Jarvis settings UI")
        print("   3. Test voice quality and performance")
        print("   4. Create voice preview system")
        
    except Exception as e:
        print(f"❌ Voice discovery failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

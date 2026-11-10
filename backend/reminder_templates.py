"""
Templates for generating safe, bounded dose reminder scripts in regional Indian languages.
Strict safety rule: Only pre-approved template scripts are voiced in cloned family voices.
"""
from typing import List, Dict, Any

TEMPLATES = {
    "te-IN": {
        "call_name": "అమ్మా", # Default affectionate call name
        "slots": {
            "morning": "ఉదయం",
            "afternoon": "మధ్యాహ్నం",
            "night": "రాత్రి"
        },
        "food": {
            "before": "అల్పాహారం/భోజనం కంటే ముందు ఖాళీ కడుపుతో",
            "after": "భోజనం తర్వాత",
            "with": "భోజనంతో పాటు",
            "unknown": "సమయానికి"
        },
        "sentence": "{call_name}, ఇది మీ మందుల సమయం. {slot} {food} {med_name} {dose} వేసుకోండి. నీరు ఎక్కువగా తాగండి."
    },
    "hi-IN": {
        "call_name": "अम्मा",
        "slots": {
            "morning": "सुबह",
            "afternoon": "दोपहर",
            "night": "रात को"
        },
        "food": {
            "before": "खाने से पहले खाली पेट",
            "after": "खाना खाने के बाद",
            "with": "खाने के साथ",
            "unknown": "समय पर"
        },
        "sentence": "{call_name}, यह आपकी दवा का समय है। {slot} {food} {med_name} {dose} ले लीजिए। पानी जरूर पीजिए।"
    },
    "ta-IN": {
        "call_name": "அம்மா",
        "slots": {
            "morning": "காலை",
            "afternoon": "மதியம்",
            "night": "இரவு"
        },
        "food": {
            "before": "உணவுக்கு முன் வெறும் வயிற்றில்",
            "after": "உணவுக்கு பின்",
            "with": "உணவோடு",
            "unknown": "சரியான நேரத்தில்"
        },
        "sentence": "{call_name}, இது உங்கள் மருந்து நேரம். {slot} {food} {med_name} {dose} சாப்பிடுங்கள்."
    },
    "kn-IN": {
        "call_name": "ಅಮ್ಮಾ",
        "slots": {
            "morning": "ಮುಂಜಾನೆ",
            "afternoon": "ಮಧ್ಯಾಹ್ನ",
            "night": "ರಾತ್ರಿ"
        },
        "food": {
            "before": "ಊಟಕ್ಕಿಂತ ಮೊದಲು ಖಾಲಿ ಹೊಟ್ಟೆಯಲ್ಲಿ",
            "after": "ಊಟದ ನಂತರ",
            "with": "ಊಟದ ಜೊತೆಗೆ",
            "unknown": "ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ"
        },
        "sentence": "{call_name}, ಇದು ನಿಮ್ಮ ಔಷಧಿ ಸಮಯ. {slot} {food} {med_name} {dose} ತೆಗೆದುಕೊಳ್ಳಿ."
    },
    "bn-IN": {
        "call_name": "মা",
        "slots": {
            "morning": "সকালে",
            "afternoon": "দুপুরে",
            "night": "রাতে"
        },
        "food": {
            "before": "খাবারের আগে খালি পেটে",
            "after": "খাবার খাওয়ার পর",
            "with": "খাবারের সাথে",
            "unknown": "সময়মতো"
        },
        "sentence": "{call_name}, এটা আপনার ওষুধের সময়। {slot} {food} {med_name} {dose} খেয়ে নিন।"
    },
    "mr-IN": {
        "call_name": "आई",
        "slots": {
            "morning": "सकाळी",
            "afternoon": "दुपारी",
            "night": "रात्री"
        },
        "food": {
            "before": "जेवणापूर्वी रिकाम्या पोटी",
            "after": "जेवणानंतर",
            "with": "जेवणासोबत",
            "unknown": "वेळेवर"
        },
        "sentence": "{call_name}, ही औषधाची वेळ झाली आहे. {slot} {food} {med_name} {dose} घ्या."
    },
    "gu-IN": {
        "call_name": "બા",
        "slots": {
            "morning": "સવારે",
            "afternoon": "બપોરે",
            "night": "રાત્રે"
        },
        "food": {
            "before": "જમ્યા પહેલા ખાલી પેટે",
            "after": "જમ્યા પછી",
            "with": "જમવા સાથે",
            "unknown": "સમયસર"
        },
        "sentence": "{call_name}, આ દવા લેવાનો સમય છે. {slot} {food} {med_name} {dose} લો."
    },
    "ml-IN": {
        "call_name": "അമ്മേ",
        "slots": {
            "morning": "രാവിലെ",
            "afternoon": "ഉച്ചയ്ക്ക്",
            "night": "രാത്രിയിൽ"
        },
        "food": {
            "before": "ഭക്ഷണത്തിന് മുൻപ്",
            "after": "ഭക്ഷണത്തിന് ശേഷം",
            "with": "ഭക്ഷണത്തോടൊപ്പം",
            "unknown": "കൃത്യസമയത്ത്"
        },
        "sentence": "{call_name}, മരുന്ന് കഴിക്കാനുള്ള സമയമായി. {slot} {food} {med_name} {dose} കഴിക്കൂ."
    },
    "pa-IN": {
        "call_name": "ਮਾਤਾ ਜੀ",
        "slots": {
            "morning": "ਸਵੇਰੇ",
            "afternoon": "ਦੁਪਹਿਰੇ",
            "night": "ਰਾਤ ਨੂੰ"
        },
        "food": {
            "before": "ਖਾਣੇ ਤੋਂ ਪਹਿਲਾਂ ਖਾਲੀ ਪੇਟ",
            "after": "ਰੋਟੀ ਖਾਣ ਤੋਂ ਬਾਅਦ",
            "with": "ਖਾਣੇ ਦੇ ਨਾਲ",
            "unknown": "ਸਮੇਂ ਸਿਰ"
        },
        "sentence": "{call_name}, ਇਹ ਦਵਾਈ ਲੈਣ ਦਾ ਵੇਲਾ ਹੈ। {slot} {food} {med_name} {dose} ਲੈ ਲਵੋ ਜੀ।"
    },
    "en-IN": {
        "call_name": "Amma",
        "slots": {
            "morning": "in the Morning",
            "afternoon": "in the Afternoon",
            "night": "at Night"
        },
        "food": {
            "before": "before food on an empty stomach",
            "after": "after meals",
            "with": "with meals",
            "unknown": "on time"
        },
        "sentence": "{call_name}, it is time for your medicine. Please take {med_name} ({dose}) {slot} {food}. Drink sufficient water."
    }
}

def generate_reminder_proposals(
    medicines: List[Dict[str, Any]],
    lang: str = "te-IN",
    patient_call_name: str = "Amma"
) -> List[Dict[str, Any]]:
    """
    Generate proposed dose reminders grouped by slot (morning, afternoon, night).
    Returns list of dicts that can be reviewed and approved by the user/family member.
    """
    cfg = TEMPLATES.get(lang, TEMPLATES["te-IN"])
    call_name = patient_call_name.strip() or cfg["call_name"]

    proposals = []
    
    # Track medicines per slot
    slot_buckets = {
        "morning": [],
        "afternoon": [],
        "night": []
    }

    for med in medicines:
        name = med.get("name", "Medicine")
        strength = med.get("strength", "")
        med_label = f"{name} {strength}".strip()
        dose = med.get("dose", "1 tablet")
        food_pref = med.get("with_food", "after")
        food_text = cfg["food"].get(food_pref, cfg["food"]["after"])
        
        timings = med.get("timing", ["morning"])
        for t in timings:
            if t in slot_buckets:
                slot_buckets[t].append({
                    "med_name": med_label,
                    "dose": dose,
                    "food": food_text
                })

    # Build scripts per slot
    slot_order = [("morning", "Morning Dose / ఉదయకాల మోతాదు"),
                  ("afternoon", "Afternoon Dose / మధ్యాహ్న మోతాదు"),
                  ("night", "Night Dose / రాత్రి మోతాదు")]

    for slot_key, slot_title in slot_order:
        items = slot_buckets[slot_key]
        if not items:
            continue
        
        med_names = ", ".join([it["med_name"] for it in items])
        # Build composite script
        slot_word = cfg["slots"].get(slot_key, slot_key)
        
        script_parts = []
        for it in items:
            part = cfg["sentence"].format(
                call_name=call_name,
                slot=slot_word,
                food=it["food"],
                med_name=it["med_name"],
                dose=it["dose"]
            )
            script_parts.append(part)
            
        full_script = " ".join(script_parts)

        proposals.append({
            "slot": slot_key,
            "title": slot_title,
            "medicines_summary": med_names,
            "items_count": len(items),
            "script_text": full_script
        })

    return proposals

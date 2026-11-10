"""
Templates for generating safe, bounded dose reminder scripts in regional Indian languages.
Strict safety rule: Only pre-approved template scripts are voiced in cloned family voices.
Eliminates redundant repetitions of greetings when multiple medicines are taken in the same slot.
"""
from typing import List, Dict, Any

TEMPLATES = {
    "te-IN": {
        "call_name": "అమ్మా",
        "intro": "{call_name}, ఇది మీ {slot} మందుల సమయం.",
        "slots": {
            "morning": "ఉదయం",
            "afternoon": "మధ్యాహ్నం",
            "night": "రాత్రి"
        },
        "food": {
            "before": "అల్పాహారం కంటే ముందు ఖాళీ కడుపుతో",
            "after": "భోజనం తర్వాత",
            "with": "భోజనంతో పాటు",
            "unknown": "సమయానికి"
        },
        "item": "{food} {med_name} {dose} వేసుకోండి.",
        "closing": "నీరు ఎక్కువగా తాగండి."
    },
    "hi-IN": {
        "call_name": "अम्मा",
        "intro": "{call_name}, यह आपकी {slot} की दवा का समय है।",
        "slots": {
            "morning": "सुबह",
            "afternoon": "दोपहर",
            "night": "रात"
        },
        "food": {
            "before": "खाने से पहले खाली पेट",
            "after": "खाना खाने के बाद",
            "with": "खाने के साथ",
            "unknown": "समय पर"
        },
        "item": "{food} {med_name} {dose} ले लीजिए।",
        "closing": "पानी जरूर पीजिए।"
    },
    "ta-IN": {
        "call_name": "அம்மா",
        "intro": "{call_name}, இது உங்கள் {slot} மருந்து நேரம்.",
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
        "item": "{food} {med_name} {dose} சாப்பிடுங்கள்.",
        "closing": "நிறைய தண்ணீர் குடியுங்கள்."
    },
    "kn-IN": {
        "call_name": "ಅಮ್ಮಾ",
        "intro": "{call_name}, ಇದು ನಿಮ್ಮ {slot} ಔಷಧಿ ಸಮಯ.",
        "slots": {
            "morning": "ಮುಂಜಾನೆಯ",
            "afternoon": "ಮಧ್ಯಾಹ್ನದ",
            "night": "ರಾತ್ರಿಯ"
        },
        "food": {
            "before": "ಊಟಕ್ಕಿಂತ ಮೊದಲು ಖಾಲಿ ಹೊಟ್ಟೆಯಲ್ಲಿ",
            "after": "ಊಟದ ನಂತರ",
            "with": "ಊಟದ ಜೊತೆಗೆ",
            "unknown": "ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ"
        },
        "item": "{food} {med_name} {dose} ತೆಗೆದುಕೊಳ್ಳಿ.",
        "closing": "ನೀರನ್ನು ಹೆಚ್ಚಾಗಿ ಕುಡಿಯಿರಿ."
    },
    "bn-IN": {
        "call_name": "মা",
        "intro": "{call_name}, এটা আপনার {slot} ওষুধের সময়।",
        "slots": {
            "morning": "সকালের",
            "afternoon": "দুপুরের",
            "night": "রাতের"
        },
        "food": {
            "before": "খাবারের আগে খালি পেটে",
            "after": "খাবার খাওয়ার পর",
            "with": "খাবারের সাথে",
            "unknown": "সময়মতো"
        },
        "item": "{food} {med_name} {dose} খেয়ে নিন।",
        "closing": "বেশি করে জল খাবেন।"
    },
    "mr-IN": {
        "call_name": "आई",
        "intro": "{call_name}, ही तुमची {slot} औषधाची वेळ झाली आहे.",
        "slots": {
            "morning": "सकाळच्या",
            "afternoon": "दुपारच्या",
            "night": "रात्रीच्या"
        },
        "food": {
            "before": "जेवणापूर्वी रिकाम्या पोटी",
            "after": "जेवणानंतर",
            "with": "जेवणासोबत",
            "unknown": "वेळेवर"
        },
        "item": "{food} {med_name} {dose} घ्या.",
        "closing": "भरपूर पाणी प्या."
    },
    "gu-IN": {
        "call_name": "બા",
        "intro": "{call_name}, આ તમારા {slot} દવા લેવાનો સમય છે.",
        "slots": {
            "morning": "સવારની",
            "afternoon": "બપોરની",
            "night": "રાતની"
        },
        "food": {
            "before": "જમ્યા પહેલા ખાલી પેટે",
            "after": "જમ્યા પછી",
            "with": "જમવા સાથે",
            "unknown": "સમયસર"
        },
        "item": "{food} {med_name} {dose} લો.",
        "closing": "ખૂબ પાણી પીજો."
    },
    "ml-IN": {
        "call_name": "അമ്മേ",
        "intro": "{call_name}, ഇത് നിങ്ങളുടെ {slot} മരുന്ന് കഴിക്കാനുള്ള സമയമാണ്.",
        "slots": {
            "morning": "രാവിലത്തെ",
            "afternoon": "ഉച്ചയ്ക്കത്തെ",
            "night": "രാത്രിയിലെ"
        },
        "food": {
            "before": "ഭക്ഷണത്തിന് മുൻപ്",
            "after": "ഭക്ഷണത്തിന് ശേഷം",
            "with": "ഭക്ഷണത്തോടൊപ്പം",
            "unknown": "കൃത്യസമയത്ത്"
        },
        "item": "{food} {med_name} {dose} കഴിക്കൂ.",
        "closing": "ധാരാളം വെള്ളം കുടിക്കണം."
    },
    "pa-IN": {
        "call_name": "ਮਾਤਾ ਜੀ",
        "intro": "{call_name}, ਇਹ ਤੁਹਾਡੀ {slot} ਦਵਾਈ ਲੈਣ ਦਾ ਵੇਲਾ ਹੈ।",
        "slots": {
            "morning": "ਸਵੇਰ ਦੀ",
            "afternoon": "ਦੁਪਹਿਰ ਦੀ",
            "night": "ਰਾਤ ਦੀ"
        },
        "food": {
            "before": "ਖਾਣੇ ਤੋਂ ਪਹਿਲਾਂ ਖਾਲੀ ਪੇਟ",
            "after": "ਰੋਟੀ ਖਾਣ ਤੋਂ ਬਾਅਦ",
            "with": "ਖਾਣੇ ਦੇ ਨਾਲ",
            "unknown": "ਸਮੇਂ ਸਿਰ"
        },
        "item": "{food} {med_name} {dose} ਲੈ ਲਵੋ ਜੀ।",
        "closing": "ਪਾਣੀ ਜ਼ਿਆਦਾ ਪੀਣਾ ਜੀ।"
    },
    "en-IN": {
        "call_name": "Amma",
        "intro": "{call_name}, it is time for your {slot} medicines.",
        "slots": {
            "morning": "morning",
            "afternoon": "afternoon",
            "night": "night"
        },
        "food": {
            "before": "before food on an empty stomach",
            "after": "after meals",
            "with": "with meals",
            "unknown": "on time"
        },
        "item": "Please take {med_name} ({dose}) {food}.",
        "closing": "Drink sufficient water."
    }
}

def generate_reminder_proposals(
    medicines: List[Dict[str, Any]],
    lang: str = "te-IN",
    patient_call_name: str = "Amma"
) -> List[Dict[str, Any]]:
    """
    Generate clean, natural dose reminder scripts grouped by slot (morning, afternoon, night).
    The greeting/intro is spoken ONCE per slot instead of repeating for every medicine.
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
        # If dose is already contained in medicine label (e.g. 'Cough Syrup 10 ml' with dose '10 ml'), avoid saying '10 ml 10 ml'
        display_dose = "" if dose.lower() in med_label.lower() else dose
        food_pref = med.get("with_food", "after")
        food_text = cfg["food"].get(food_pref, cfg["food"]["after"])
        
        timings = med.get("timing", ["morning"])
        for t in timings:
            if t in slot_buckets:
                slot_buckets[t].append({
                    "med_name": med_label,
                    "dose": display_dose,
                    "food": food_text
                })

    slot_order = [
        ("morning", "Morning Dose / ఉదయకాల మోతాదు"),
        ("afternoon", "Afternoon Dose / మధ్యాహ్న మోతాదు"),
        ("night", "Night Dose / రాత్రి మోతాదు")
    ]

    for slot_key, slot_title in slot_order:
        items = slot_buckets[slot_key]
        if not items:
            continue
        
        med_names = ", ".join([it["med_name"] for it in items])
        slot_word = cfg["slots"].get(slot_key, slot_key)
        intro_part = cfg["intro"].format(call_name=call_name, slot=slot_word)

        items_parts = []
        for it in items:
            part = cfg["item"].format(
                food=it["food"],
                med_name=it["med_name"],
                dose=it["dose"]
            )
            items_parts.append(part.strip())

        closing_part = cfg.get("closing", "")
        full_script = f"{intro_part} {' '.join(items_parts)} {closing_part}".strip()

        proposals.append({
            "slot": slot_key,
            "title": slot_title,
            "medicines_summary": med_names,
            "items_count": len(items),
            "script_text": full_script
        })

    return proposals

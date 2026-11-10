/**
 * Dawai Saathi - Mobile-first Frontend Application
 * Handles:
 * 1. Multi-language switching & persistence
 * 2. Prescription photo upload & LLM vision analysis
 * 3. Voice Q&A recording & playback via Gnani STT/TTS
 * 4. Family voice enrollment (with explicit consent) & cloned voice reminders
 */

// State Management
const state = {
  currentLang: localStorage.getItem("dawai_lang") || "te-IN",
  activePrescription: null,
  activePrescriptionId: null,
  enrolledVoices: [],
  selectedVoiceId: null,
  currentReminders: [],
  proposedScripts: [],
  // Recorders
  mediaRecorderQna: null,
  audioChunksQna: [],
  isRecordingQna: false,
  timerIntervalQna: null,
  recordingSecondsQna: 0,

  mediaRecorderFamily: null,
  audioChunksFamily: [],
  isRecordingFamily: false,
  timerIntervalFamily: null,
  recordingSecondsFamily: 0,
  familyRecordedBlob: null
};

// Regional prompt sentences to read during voice enrollment
const VOICE_READING_PROMPTS = {
  "te-IN": "అమ్మా, మీరు సమయానికి మందులు వేసుకోండి. భోజనం తర్వాత మాత్ర తీసుకోండి. నీరు ఎక్కువగా తాగండి, మీ ఆరోగ్యం జాగ్రత్త.",
  "hi-IN": "अम्मा, आप समय पर दवाइयां ले लीजिए। खाना खाने के बाद गोली लें। पानी ज्यादा पिएं, अपना ध्यान रखें।",
  "ta-IN": "அம்மா, நேரத்திற்கு மருந்துகளை சாப்பிடுங்கள். உணவுக்குப் பின் மாத்திரைகளை எடுத்துக் கொள்ளுங்கள். நிறைய தண்ணீர் குடியுங்கள்.",
  "kn-IN": "ಅಮ್ಮಾ, ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ಔಷಧಿ ತೆಗೆದುಕೊಳ್ಳಿ. ಊಟದ ನಂತರ ಮಾತ್ರೆ ನುಂಗಿ. ನೀರನ್ನು ಹೆಚ್ಚಾಗಿ ಕುಡಿಯಿರಿ.",
  "bn-IN": "মা, সময়মতো ওষুধগুলো খেয়ে নেবেন। খাওয়ার পরে ট্যাবলেট খাবেন। বেশি করে জল খাবেন, নিজের যত্ন নেবেন।",
  "mr-IN": "आई, वेळेवर औषधे घ्या. जेवणानंतर गोळी घ्या. भरपूर पाणी प्या आणि स्वतःची काळजी घ्या.",
  "gu-IN": "બા, સમયસર દવા લઈ લેજો. જમ્યા પછી ગોળી લેજો. ખૂબ પાણી પીજો અને તમારું ધ્યાન રાખજો.",
  "ml-IN": "അമ്മേ, കൃത്യസമയത്ത് മരുന്ന് കഴിക്കണം. ഭക്ഷണത്തിന് ശേഷം ഗുളിക കഴിക്കുക. ധാരാളം വെള്ളം കുടിക്കണം.",
  "pa-IN": "ਮਾਤਾ ਜੀ, ਸਮੇਂ ਸਿਰ ਦਵਾਈਆਂ ਲੈ ਲੈਣਾ ਜੀ। ਰੋਟੀ ਖਾਣ ਤੋਂ ਬਾਅਦ ਗੋਲੀ ਲਵੋ। ਪਾਣੀ ਜ਼ਿਆਦਾ ਪੀਣਾ, ਆਪਣਾ ਖਿਆल ਰੱਖਣਾ।",
  "en-IN": "Amma, please take your medicines on time. Take the tablet after lunch. Drink plenty of water and stay healthy."
};

// UI Translations for Key Headings
const UI_I18N = {
  "te-IN": {
    heroTitle: "ప్రిస్క్రిప్షన్ లేదా ల్యాబ్ రిపోర్ట్ అప్‌లోడ్ చేయండి",
    heroDesc: "మీ డాక్టర్ ప్రిస్క్రిప్షన్ ఫోటో తీయండి. మీ ప్రాంతీయ భాషలో మరియు మీ కుటుంబ సభ్యుల స్వరంలో మందుల వివరాలు వినండి.",
    loadingText: "ప్రిస్క్రిప్షన్ చదువుతున్నాము మరియు తెలుగు స్వరం సిద్ధం చేస్తున్నాము..."
  },
  "hi-IN": {
    heroTitle: "पर्चा या लैब रिपोर्ट अपलोड करें",
    heroDesc: "डॉक्टर के पर्चे का फोटो लें। हम आपकी भाषा और आपके परिवार की आवाज़ में पूरी दवाइयां समझाएंगे।",
    loadingText: "पर्चा पढ़ा जा रहा है और हिंदी आवाज़ तैयार की जा रही है..."
  },
  "en-IN": {
    heroTitle: "Upload Prescription or Lab Report",
    heroDesc: "Take a photo of your doctor's prescription. We will explain all medicines in your own language and voice.",
    loadingText: "Analyzing Prescription & Synthesizing Voice..."
  }
};

// ==========================================
// Initialization
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  initLanguage();
  initNavigation();
  initPWA();
  initScanControls();
  initQnaControls();
  initFamilyVoiceControls();
  loadRecentPrescription();
  loadFamilyVoices();
});

// Toast Notifications
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.className = `mb-4 p-3 rounded-xl text-xs font-semibold shadow-md transition-all flex items-center justify-between ${
    type === "error"
      ? "bg-red-100 text-red-900 border border-red-300"
      : type === "success"
      ? "bg-emerald-100 text-emerald-900 border border-emerald-300"
      : "bg-teal-100 text-teal-900 border border-teal-300"
  }`;
  toast.innerHTML = `<span>${message}</span><button onclick="document.getElementById('toast').classList.add('hidden')" class="ml-2 font-bold opacity-60">✕</button>`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 5000);
}

// ==========================================
// Language Switching
// ==========================================
function initLanguage() {
  const select = document.getElementById("langSelect");
  select.value = state.currentLang;
  
  select.addEventListener("change", (e) => {
    state.currentLang = e.target.value;
    localStorage.setItem("dawai_lang", state.currentLang);
    updateLanguageTexts();
    showToast(`Language updated to ${select.options[select.selectedIndex].text}`, "success");
    
    // If prescription exists, refresh reminder proposals in new language
    if (state.activePrescriptionId) {
      loadReminderProposals();
    }
  });

  updateLanguageTexts();
}

function updateLanguageTexts() {
  const promptEl = document.getElementById("voicePromptText");
  if (promptEl) {
    promptEl.textContent = `"${VOICE_READING_PROMPTS[state.currentLang] || VOICE_READING_PROMPTS["te-IN"]}"`;
  }
  const i18n = UI_I18N[state.currentLang] || UI_I18N["en-IN"];
  if (document.getElementById("heroTitle")) document.getElementById("heroTitle").textContent = i18n.heroTitle;
  if (document.getElementById("heroDesc")) document.getElementById("heroDesc").textContent = i18n.heroDesc;
  if (document.getElementById("loadingText")) document.getElementById("loadingText").textContent = i18n.loadingText;
}

// ==========================================
// Bottom Navigation Tabs
// ==========================================
function initNavigation() {
  const tabs = {
    tabScan: document.getElementById("sectionScan"),
    tabQna: document.getElementById("sectionQna"),
    tabFamily: document.getElementById("sectionFamily"),
  };

  const buttons = {
    tabScan: document.getElementById("tabScan"),
    tabQna: document.getElementById("tabQna"),
    tabFamily: document.getElementById("tabFamily"),
  };

  Object.keys(buttons).forEach((key) => {
    buttons[key].addEventListener("click", () => {
      // Hide all sections
      Object.values(tabs).forEach((sec) => sec.classList.add("hidden"));
      
      // Reset all buttons to inactive state
      Object.values(buttons).forEach((btn) => {
        btn.classList.remove("active-tab");
        const pill = btn.querySelector(".nav-pill");
        if (pill) {
          pill.classList.remove("bg-emerald-100", "text-forest-900");
          pill.classList.add("text-slate-400");
        }
        const label = btn.querySelector(".nav-label");
        if (label) {
          label.classList.remove("text-forest-900", "font-bold");
          label.classList.add("text-slate-500", "font-medium");
        }
      });

      // Activate clicked tab
      tabs[key].classList.remove("hidden");
      buttons[key].classList.add("active-tab");
      const activePill = buttons[key].querySelector(".nav-pill");
      if (activePill) {
        activePill.classList.remove("text-slate-400");
        activePill.classList.add("bg-emerald-100", "text-forest-900");
      }
      const activeLabel = buttons[key].querySelector(".nav-label");
      if (activeLabel) {
        activeLabel.classList.remove("text-slate-500", "font-medium");
        activeLabel.classList.add("text-forest-900", "font-bold");
      }
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  // CTA from Scan Result to Reminders
  document.getElementById("btnGoToReminders").addEventListener("click", () => {
    buttons.tabFamily.click();
    document.getElementById("subTabDashboard").click();
  });
}

// ==========================================
// Progressive Web App (PWA) Handler
// ==========================================
function initPWA() {
  // Register Service Worker
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js", { scope: "/" })
        .then((reg) => console.log("PWA Service Worker registered:", reg.scope))
        .catch((err) => console.warn("PWA Service Worker registration error:", err));
    });
  }

  let deferredPrompt = null;
  const installBtn = document.getElementById("btnInstallPWA");

  // Chrome / Android Install Prompt Event
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) {
      installBtn.classList.remove("hidden");
      installBtn.classList.add("flex");
    }
  });

  if (installBtn) {
    // Check if app is not already running standalone
    const isStandalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone;
    if (!isStandalone) {
      installBtn.classList.remove("hidden");
      installBtn.classList.add("flex");
    }

    installBtn.addEventListener("click", async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const choice = await deferredPrompt.userChoice;
        if (choice.outcome === "accepted") {
          installBtn.classList.add("hidden");
          deferredPrompt = null;
          showToast("Installing Dawai Saathi to your device...", "success");
        }
      } else {
        // Helpful contextual instructions for iOS vs Android
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        if (isIOS) {
          showToast("To install on iOS: Tap Share (⬆️) and select 'Add to Home Screen'", "info");
        } else {
          showToast("To install: Tap browser menu (⋮) -> 'Install App' or 'Add to Home Screen'", "info");
        }
      }
    });
  }

  window.addEventListener("appinstalled", () => {
    if (installBtn) installBtn.classList.add("hidden");
    showToast("🎉 Dawai Saathi installed! Tap icon on home screen to use.", "success");
  });
}

// ==========================================
// 1. Prescription Scanning & Display
// ==========================================
function initScanControls() {
  const fileInput = document.getElementById("rxFileInput");
  const btnSample = document.getElementById("btnSampleRx");
  const playBtn = document.getElementById("btnPlaySummary");
  const audio = document.getElementById("summaryAudioPlayer");

  fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      await uploadAndProcessRx(file);
    }
  });

  btnSample.addEventListener("click", async () => {
    await loadSamplePrescription();
  });

  // Audio Player Scrubber Controls
  playBtn.addEventListener("click", () => {
    if (!audio.src) return;
    if (audio.paused) {
      audio.play();
      playBtn.textContent = "⏸";
    } else {
      audio.pause();
      playBtn.textContent = "▶";
    }
  });

  audio.addEventListener("timeupdate", () => {
    if (!audio.duration) return;
    const cur = formatTime(audio.currentTime);
    const dur = formatTime(audio.duration);
    document.getElementById("audioCurrentTime").textContent = cur;
    document.getElementById("audioTotalTime").textContent = dur;
    const pct = (audio.currentTime / audio.duration) * 100;
    document.getElementById("audioProgressBar").style.width = `${pct}%`;
  });

  audio.addEventListener("ended", () => {
    playBtn.textContent = "▶";
    document.getElementById("audioProgressBar").style.width = "0%";
  });

  document.getElementById("audioProgressContainer").addEventListener("click", (e) => {
    if (!audio.duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    audio.currentTime = pos * audio.duration;
  });
}

async function uploadAndProcessRx(file) {
  const loading = document.getElementById("scanLoading");
  const resultContainer = document.getElementById("rxResult");

  loading.classList.remove("hidden");
  resultContainer.classList.add("hidden");

  const formData = new FormData();
  formData.append("image", file);
  formData.append("language", state.currentLang);

  try {
    const resp = await fetch("/api/scan", {
      method: "POST",
      body: formData,
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Prescription analysis failed");
    }
    const res = await resp.json();
    renderPrescription(res);
    showToast("Prescription analyzed & regional voice summary ready!", "success");
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  } finally {
    loading.classList.add("hidden");
  }
}

async function loadSamplePrescription() {
  const loading = document.getElementById("scanLoading");
  const resultContainer = document.getElementById("rxResult");
  loading.classList.remove("hidden");
  resultContainer.classList.add("hidden");

  try {
    // Fetch generated sample image from backend
    const sampleResp = await fetch("/samples/sample_prescription.png");
    let blob;
    if (sampleResp.ok) {
      blob = await sampleResp.blob();
    } else {
      // Fallback empty canvas if file path not served
      const canvas = document.createElement("canvas");
      canvas.width = 600;
      canvas.height = 800;
      blob = await new Promise((r) => canvas.toBlob(r, "image/png"));
    }

    const formData = new FormData();
    formData.append("image", blob, "sample_prescription.png");
    formData.append("language", state.currentLang);

    const resp = await fetch("/api/scan", {
      method: "POST",
      body: formData,
    });
    if (!resp.ok) throw new Error("Sample scan failed");
    const res = await resp.json();
    renderPrescription(res);
    showToast("Sample Prescription loaded successfully!", "success");
  } catch (err) {
    showToast(`Error loading sample: ${err.message}`, "error");
  } finally {
    loading.classList.add("hidden");
  }
}

function renderPrescription(res) {
  state.activePrescription = res;
  state.activePrescriptionId = res.prescription_id;

  const resultContainer = document.getElementById("rxResult");
  resultContainer.classList.remove("hidden");

  // Update QnA context status
  document.getElementById("qnaRxStatus").innerHTML = `Prescription: <strong class="text-teal-700">${res.prescription_id.substring(0, 8)}</strong>`;

  // Spoken summary audio setup
  const preview = document.getElementById("spokenSummaryPreview");
  preview.textContent = `"${res.spoken_summary}"`;

  const audio = document.getElementById("summaryAudioPlayer");
  audio.src = res.audio_url;
  audio.load();

  // Medicines list rendering
  const medList = document.getElementById("medicineCardsList");
  medList.innerHTML = "";
  const meds = res.data.medicines || [];
  document.getElementById("medCount").textContent = meds.length;

  meds.forEach((m) => {
    const card = document.createElement("div");
    card.className = "med-card p-4 space-y-2.5";

    // Timing Badges
    const timingBadges = (m.timing || ["morning"])
      .map((t) => {
        if (t === "morning") return `<span class="slot-badge-morning text-[11px] font-bold px-2.5 py-1 rounded-lg">🌅 Morning</span>`;
        if (t === "afternoon") return `<span class="slot-badge-afternoon text-[11px] font-bold px-2.5 py-1 rounded-lg">☀️ Afternoon</span>`;
        if (t === "night") return `<span class="slot-badge-night text-[11px] font-bold px-2.5 py-1 rounded-lg">🌙 Night</span>`;
        return `<span class="bg-slate-100 text-slate-700 text-[11px] font-bold px-2 py-0.5 rounded-lg">${t}</span>`;
      })
      .join(" ");

    // Food relation badge
    const foodClass = m.with_food === "before" ? "bg-saffron-100 text-saffron-800 border border-saffron-200" : "bg-forest-100 text-forest-800 border border-emerald-200";
    const foodText = m.with_food === "before" ? "🍽️ Before Food / ఖాళీ కడుపుతో" : "🍲 After Food / భోజనం తర్వాత";

    card.innerHTML = `
      <div class="flex items-start justify-between">
        <div>
          <h4 class="font-extrabold text-slate-900 text-sm tracking-tight">${m.name} <span class="text-forest-700 font-bold text-xs bg-forest-50 px-2 py-0.5 rounded-md border border-emerald-200 ml-1">${m.strength}</span></h4>
          <p class="text-xs text-slate-500 font-medium mt-1">💊 ${m.dose} • ${m.frequency_per_day} dose(s) daily • <span class="text-forest-800 font-semibold">For ${m.duration_days} days</span></p>
        </div>
        <span class="text-[10px] font-bold px-2.5 py-1 rounded-full ${foodClass}">${foodText}</span>
      </div>
      <div class="flex items-center space-x-2 pt-1">
        ${timingBadges}
      </div>
      ${m.purpose_plain ? `<p class="text-xs text-slate-600 bg-slate-50 rounded-xl p-2.5 border border-slate-200/60 leading-relaxed">💡 <em>${m.purpose_plain}</em></p>` : ""}
    `;
    medList.appendChild(card);
  });

  // Unclear items box (yellow)
  const unclearBox = document.getElementById("unclearBox");
  const unclearList = document.getElementById("unclearList");
  unclearList.innerHTML = "";
  if (res.data.unclear_items && res.data.unclear_items.length > 0) {
    unclearBox.classList.remove("hidden");
    res.data.unclear_items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      unclearList.appendChild(li);
    });
  } else {
    unclearBox.classList.add("hidden");
  }

  // Doctor warning list (red)
  const docList = document.getElementById("doctorWarningList");
  docList.innerHTML = "";
  const warnings = res.data.see_doctor_if || [
    "High fever exceeding 103°F",
    "Breathing difficulty or chest pain",
    "Symptoms persist after complete course"
  ];
  warnings.forEach((w) => {
    const li = document.createElement("li");
    li.textContent = w;
    docList.appendChild(li);
  });

  // Pre-load reminder proposals for the Family Voice tab
  loadReminderProposals();
}

async function loadRecentPrescription() {
  try {
    const resp = await fetch("/api/prescriptions");
    if (!resp.ok) return;
    const list = await resp.json();
    if (list.length > 0) {
      renderPrescription({
        prescription_id: list[0].id,
        language: list[0].language,
        data: list[0].data,
        spoken_summary: list[0].spoken_summary || list[0].data.spoken_summary,
        audio_url: `/api/audio/${list[0].audio_filename}`
      });
    }
  } catch (e) {
    console.log("No previous prescription:", e);
  }
}

// ==========================================
// 2. Voice Q&A (Prisma v3.0 STT + Contextual Answer)
// ==========================================
function initQnaControls() {
  const btnRecord = document.getElementById("btnRecordQuestion");
  const timerEl = document.getElementById("recordingTimer");
  const pulseEl = document.getElementById("micPulse");
  const micIcon = document.getElementById("micIcon");

  btnRecord.addEventListener("click", async () => {
    if (!state.activePrescriptionId) {
      showToast("Please upload or load a prescription first before asking questions.", "error");
      return;
    }

    if (!state.isRecordingQna) {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        state.audioChunksQna = [];
        state.mediaRecorderQna = new MediaRecorder(stream);

        state.mediaRecorderQna.ondataavailable = (e) => {
          if (e.data.size > 0) state.audioChunksQna.push(e.data);
        };

        state.mediaRecorderQna.onstop = async () => {
          stream.getTracks().forEach((track) => track.stop());
          const audioBlob = new Blob(state.audioChunksQna, { type: "audio/webm" });
          await submitQuestionAudio(audioBlob);
        };

        state.mediaRecorderQna.start();
        state.isRecordingQna = true;

        // Visuals
        pulseEl.classList.remove("hidden");
        micIcon.textContent = "⏹";
        btnRecord.classList.replace("bg-indigo-600", "bg-red-600");
        document.getElementById("micInstruction").textContent = "Listening... Speak your question clearly";

        // Timer
        state.recordingSecondsQna = 0;
        state.timerIntervalQna = setInterval(() => {
          state.recordingSecondsQna++;
          timerEl.textContent = formatTime(state.recordingSecondsQna);
          if (state.recordingSecondsQna >= 25) {
            // Auto stop at 25 seconds (STT limit is 30s)
            btnRecord.click();
          }
        }, 1000);
      } catch (err) {
        showToast("Microphone permission denied or not supported.", "error");
      }
    } else {
      // Stop recording
      state.isRecordingQna = false;
      clearInterval(state.timerIntervalQna);
      pulseEl.classList.add("hidden");
      micIcon.textContent = "🎙️";
      btnRecord.classList.replace("bg-red-600", "bg-indigo-600");
      document.getElementById("micInstruction").textContent = "Processing audio with Gnani Prisma...";
      state.mediaRecorderQna.stop();
    }
  });

  // Voice answer playback
  const playQnaBtn = document.getElementById("btnPlayQnaAudio");
  const qnaAudio = document.getElementById("qnaAudioPlayer");
  playQnaBtn.addEventListener("click", () => {
    if (!qnaAudio.src) return;
    if (qnaAudio.paused) {
      qnaAudio.play();
      playQnaBtn.textContent = "⏸";
    } else {
      qnaAudio.pause();
      playQnaBtn.textContent = "▶";
    }
  });
  qnaAudio.addEventListener("ended", () => (playQnaBtn.textContent = "▶"));
}

async function submitQuestionAudio(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "question.webm");
  formData.append("prescription_id", state.activePrescriptionId);
  formData.append("language", "indic-auto");
  formData.append("use_family_voice", document.getElementById("chkUseFamilyVoiceQna").checked);

  try {
    const resp = await fetch("/api/ask", {
      method: "POST",
      body: formData,
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Q&A processing failed");
    }
    const res = await resp.json();

    // Render Q&A result
    const qnaCard = document.getElementById("qnaResultCard");
    qnaCard.classList.remove("hidden");
    document.getElementById("qnaTranscript").textContent = `"${res.transcript || 'No transcript detected'}"`;
    document.getElementById("detectedLangBadge").textContent = res.detected_language || state.currentLang;
    document.getElementById("qnaAnswerText").textContent = res.answer_text;

    // Load and auto-play audio answer
    const qnaAudio = document.getElementById("qnaAudioPlayer");
    qnaAudio.src = res.audio_url;
    qnaAudio.load();
    qnaAudio.play().catch(() => {});
    document.getElementById("btnPlayQnaAudio").textContent = "⏸";

    document.getElementById("micInstruction").textContent = "Tap microphone to ask another question";
    showToast("Answer generated strictly from your prescription!", "success");
  } catch (err) {
    showToast(`Q&A Error: ${err.message}`, "error");
    document.getElementById("micInstruction").textContent = "Tap microphone to try again";
  }
}

// ==========================================
// 3. Family Voice Enrollment & Cloned Reminders
// ==========================================
function initFamilyVoiceControls() {
  const subEnroll = document.getElementById("subTabEnroll");
  const subDash = document.getElementById("subTabDashboard");
  const panelEnroll = document.getElementById("panelEnroll");
  const panelDash = document.getElementById("panelDashboard");

  subEnroll.addEventListener("click", () => {
    subEnroll.className = "flex-1 py-2 text-center rounded-lg bg-white text-forest-900 shadow-sm transition font-bold";
    subDash.className = "flex-1 py-2 text-center rounded-lg text-slate-500 hover:text-forest-900 transition font-semibold";
    panelEnroll.classList.remove("hidden");
    panelDash.classList.add("hidden");
  });

  subDash.addEventListener("click", () => {
    subDash.className = "flex-1 py-2 text-center rounded-lg bg-white text-forest-900 shadow-sm transition font-bold";
    subEnroll.className = "flex-1 py-2 text-center rounded-lg text-slate-500 hover:text-forest-900 transition font-semibold";
    panelDash.classList.remove("hidden");
    panelEnroll.classList.add("hidden");
    loadRemindersDashboard();
  });

  // Recording Family Voice
  const btnFamilyMic = document.getElementById("btnRecordFamilyVoice");
  const familyPulse = document.getElementById("familyMicPulse");
  const familyIcon = document.getElementById("familyMicIcon");
  const timerFamily = document.getElementById("familyRecordingTimer");
  const previewDiv = document.getElementById("familyAudioPreview");
  const player = document.getElementById("familyAudioPlayer");

  btnFamilyMic.addEventListener("click", async () => {
    if (!state.isRecordingFamily) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        state.audioChunksFamily = [];
        state.mediaRecorderFamily = new MediaRecorder(stream);

        state.mediaRecorderFamily.ondataavailable = (e) => {
          if (e.data.size > 0) state.audioChunksFamily.push(e.data);
        };

        state.mediaRecorderFamily.onstop = () => {
          stream.getTracks().forEach((track) => track.stop());
          state.familyRecordedBlob = new Blob(state.audioChunksFamily, { type: "audio/webm" });
          previewDiv.classList.remove("hidden");
          player.src = URL.createObjectURL(state.familyRecordedBlob);
        };

        state.mediaRecorderFamily.start();
        state.isRecordingFamily = true;
        familyPulse.classList.remove("hidden");
        familyIcon.textContent = "⏹";
        btnFamilyMic.classList.replace("bg-purple-600", "bg-red-600");

        state.recordingSecondsFamily = 0;
        state.timerIntervalFamily = setInterval(() => {
          state.recordingSecondsFamily++;
          timerFamily.textContent = `${formatTime(state.recordingSecondsFamily)} (Target: 10-20s)`;
        }, 1000);
      } catch (err) {
        showToast("Microphone error: " + err.message, "error");
      }
    } else {
      state.isRecordingFamily = false;
      clearInterval(state.timerIntervalFamily);
      familyPulse.classList.add("hidden");
      familyIcon.textContent = "🎙️";
      btnFamilyMic.classList.replace("bg-red-600", "bg-purple-600");
      state.mediaRecorderFamily.stop();

      if (state.recordingSecondsFamily < 5) {
        showToast("Notice: Audio under 5 seconds may give lower voice clone fidelity.", "info");
      }
    }
  });

  // Upload Audio File for Voice Cloning
  const fileInput = document.getElementById("familyFileInput");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        state.familyRecordedBlob = file;
        previewDiv.classList.remove("hidden");
        player.src = URL.createObjectURL(file);
        const label = document.getElementById("familyAudioPreviewLabel");
        if (label) label.textContent = `Selected file: ${file.name}`;
        document.getElementById("familyRecordingTimer").textContent = "Audio file loaded!";
        showToast(`Loaded voice file: ${file.name}`, "success");
      }
    });
  }

  // One-click Sample Voice Loader
  const btnSampleVoice = document.getElementById("btnUseSampleVoice");
  if (btnSampleVoice) {
    btnSampleVoice.addEventListener("click", async () => {
      try {
        const resp = await fetch("/samples/reference_speech.wav");
        if (!resp.ok) throw new Error("Could not fetch sample voice file");
        const blob = await resp.blob();
        state.familyRecordedBlob = blob;
        previewDiv.classList.remove("hidden");
        player.src = URL.createObjectURL(blob);
        const label = document.getElementById("familyAudioPreviewLabel");
        if (label) label.textContent = "Pre-loaded Sample Voice (6s clean speech)";
        document.getElementById("familyRecordingTimer").textContent = "Sample Voice Loaded (00:06)";
        showToast("Sample voice loaded! Check consent box and save.", "success");
      } catch (e) {
        showToast("Error loading sample voice: " + e.message, "error");
      }
    });
  }

  // Save Voice Profile with Mandatory Consent
  document.getElementById("btnSaveFamilyVoice").addEventListener("click", async () => {
    const consent = document.getElementById("chkFamilyConsent").checked;
    if (!consent) {
      showToast("Consent Required: Please tick the consent box to proceed.", "error");
      return;
    }

    if (!state.familyRecordedBlob) {
      showToast("Please record your voice first (10-20s).", "error");
      return;
    }

    const name = document.getElementById("voiceFamilyName").value.trim() || "Relative";
    const patientName = document.getElementById("voiceCallName").value.trim() || "Amma";

    const formData = new FormData();
    formData.append("audio", state.familyRecordedBlob, "family_voice.webm");
    formData.append("name", name);
    formData.append("patient_name", patientName);
    formData.append("language", state.currentLang);
    formData.append("consent", "true");

    showToast("Extracting Voice Clone Embedding via Gnani AI...", "info");
    try {
      const resp = await fetch("/api/family/voice", {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Failed to save voice profile");
      }
      const data = await resp.json();
      state.selectedVoiceId = data.voice_id;
      showToast(`Success! Voice cloned for ${name}.`, "success");
      await loadFamilyVoices();

      // Automatically switch to Reminders dashboard
      subDash.click();
    } catch (e) {
      showToast(`Voice Cloning Error: ${e.message}`, "error");
    }
  });

  // Synthesize Approved Reminders Button
  document.getElementById("btnGenerateAllClonedAudio").addEventListener("click", async () => {
    await synthesizeClonedReminders();
  });
}

async function loadFamilyVoices() {
  const container = document.getElementById("enrolledVoicesList");
  try {
    const resp = await fetch("/api/family/voices");
    if (!resp.ok) return;
    const voices = await resp.json();
    state.enrolledVoices = voices;

    if (voices.length === 0) {
      container.innerHTML = `<p class="text-xs text-slate-400 italic">No family voices enrolled yet. Record above to activate cloned reminders.</p>`;
      return;
    }

    // Set default selected voice
    if (!state.selectedVoiceId && voices.length > 0) {
      state.selectedVoiceId = voices[0].id;
    }

    container.innerHTML = voices
      .map(
        (v) => `
        <div class="flex items-center justify-between p-3 rounded-xl border ${
          state.selectedVoiceId === v.id ? "bg-purple-50 border-purple-300" : "bg-slate-50 border-slate-200"
        }">
          <div class="flex items-center space-x-2.5">
            <span class="text-2xl">🗣️</span>
            <div>
              <p class="text-xs font-bold text-slate-800">${v.name} <span class="text-[10px] text-purple-700 font-semibold">(${v.patient_name})</span></p>
              <p class="text-[10px] text-slate-500">Consent verified • ${new Date(v.consent_timestamp).toLocaleDateString()}</p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button onclick="selectVoice('${v.id}')" class="text-xs font-bold px-2 py-1 rounded ${
          state.selectedVoiceId === v.id ? "bg-purple-600 text-white" : "bg-slate-200 text-slate-700"
        }">
              ${state.selectedVoiceId === v.id ? "Active" : "Use"}
            </button>
            <button onclick="deleteVoice('${v.id}')" class="text-xs text-red-500 hover:text-red-700 font-bold p-1">
              🗑️
            </button>
          </div>
        </div>
      `
      )
      .join("");
  } catch (err) {
    console.error("Error loading voices:", err);
  }
}

window.selectVoice = function (id) {
  state.selectedVoiceId = id;
  loadFamilyVoices();
  showToast("Active reminder voice selected.", "info");
};

window.deleteVoice = async function (id) {
  if (!confirm("Are you sure you want to permanently delete this voice clone embedding?")) return;
  try {
    const resp = await fetch(`/api/family/voice/${id}`, { method: "DELETE" });
    if (!resp.ok) throw new Error("Delete failed");
    if (state.selectedVoiceId === id) state.selectedVoiceId = null;
    showToast("Voice clone embedding deleted permanently.", "success");
    await loadFamilyVoices();
  } catch (e) {
    showToast("Delete error: " + e.message, "error");
  }
};

// ==========================================
// Reminder Proposals & Approval
// ==========================================
async function loadReminderProposals() {
  if (!state.activePrescriptionId) return;

  const proposalsContainer = document.getElementById("proposalsList");
  const callName = document.getElementById("voiceCallName")?.value || "Amma";

  const formData = new FormData();
  formData.append("prescription_id", state.activePrescriptionId);
  formData.append("patient_call_name", callName);

  try {
    const resp = await fetch("/api/reminders/proposals", {
      method: "POST",
      body: formData,
    });
    if (!resp.ok) return;
    const proposals = await resp.json();
    state.proposedScripts = proposals;

    proposalsContainer.innerHTML = proposals
      .map(
        (p, idx) => `
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="font-bold text-teal-800 uppercase tracking-wider">${p.title}</span>
            <label class="flex items-center space-x-1 cursor-pointer">
              <input type="checkbox" id="propCheck_${idx}" checked class="rounded text-teal-600 focus:ring-teal-500">
              <span class="text-[10px] text-slate-600 font-medium">Approve</span>
            </label>
          </div>
          <p class="text-slate-800 font-medium italic" id="propScript_${idx}">"${p.script_text}"</p>
          <p class="text-[10px] text-slate-500">Covers: <strong>${p.medicines_summary}</strong></p>
        </div>
      `
      )
      .join("");
  } catch (e) {
    console.error("Proposals loading error:", e);
  }
}

async function synthesizeClonedReminders() {
  if (!state.activePrescriptionId) {
    showToast("Please load a prescription first.", "error");
    return;
  }

  showToast("Synthesizing reminders in cloned family voice...", "info");

  // Collect approved scripts
  const approvedList = [];
  state.proposedScripts.forEach((p, idx) => {
    const chk = document.getElementById(`propCheck_${idx}`);
    if (!chk || chk.checked) {
      approvedList.push({
        slot: p.slot,
        script_text: p.script_text,
        medicine_name: p.medicines_summary,
      });
    }
  });

  if (approvedList.length === 0) {
    showToast("Please approve at least one reminder script.", "error");
    return;
  }

  try {
    const payload = {
      prescription_id: state.activePrescriptionId,
      voice_id: state.selectedVoiceId,
      patient_call_name: document.getElementById("voiceCallName")?.value || "Amma",
      approved_scripts: approvedList,
    };

    const resp = await fetch("/api/reminders/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Reminder synthesis failed");
    }

    const reminders = await resp.json();
    state.currentReminders = reminders;
    renderRemindersDashboard(reminders);
    showToast("Reminders voiced with AI tag attached!", "success");
  } catch (e) {
    showToast(`Error: ${e.message}`, "error");
  }
}

async function loadRemindersDashboard() {
  if (!state.activePrescriptionId) return;

  try {
    const resp = await fetch(`/api/reminders/${state.activePrescriptionId}`);
    if (resp.ok) {
      const reminders = await resp.json();
      if (reminders.length > 0) {
        state.currentReminders = reminders;
        renderRemindersDashboard(reminders);
      } else {
        // If no reminders exist yet, load proposals
        loadReminderProposals();
      }
    }
  } catch (e) {
    console.error("Error loading reminders:", e);
  }
}

function renderRemindersDashboard(reminders) {
  const container = document.getElementById("remindersCardsList");
  if (!reminders || reminders.length === 0) {
    container.innerHTML = `<p class="text-xs text-slate-400 italic">No reminders generated yet.</p>`;
    return;
  }

  container.innerHTML = reminders
    .map((r) => {
      const isTaken = r.is_taken;
      const slotIcon = r.slot === "morning" ? "🌅" : r.slot === "afternoon" ? "☀️" : "🌙";
      
      // WhatsApp share link
      const origin = window.location.origin;
      const fullAudioUrl = `${origin}${r.audio_url}`;
      const waText = encodeURIComponent(
        `💊 *Dawai Saathi Medicine Reminder*\n${r.script_text}\n\n🔊 Listen to voice reminder: ${fullAudioUrl}`
      );
      const waUrl = `https://wa.me/?text=${waText}`;

      return `
      <div class="med-card ${
        isTaken ? "bg-emerald-50/40 border-emerald-300" : "bg-white"
      } p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2.5">
            <span class="text-2xl">${slotIcon}</span>
            <div>
              <h4 class="font-extrabold text-xs uppercase tracking-wider text-slate-800">${r.slot} Dose</h4>
              <p class="text-xs text-slate-600 font-bold">${r.medicine_name}</p>
            </div>
          </div>
          <span class="text-[10px] font-extrabold px-2.5 py-1 rounded-full ${
            isTaken ? "bg-emerald-100 text-forest-800 border border-emerald-300" : "bg-saffron-100 text-saffron-800 border border-saffron-200"
          }">
            ${isTaken ? "✓ Marked Taken" : "Pending"}
          </span>
        </div>

        <p class="text-xs text-slate-800 italic bg-slate-50 p-3 rounded-xl border border-slate-200/70 leading-relaxed font-medium">
          "${r.script_text}"
        </p>

        <!-- Actions: Play Voice, Mark Taken, WhatsApp -->
        <div class="flex items-center justify-between pt-1 text-xs">
          <div class="flex items-center space-x-2">
            <button onclick="playReminderAudio('${r.audio_url}', this)" class="w-10 h-10 bg-forest-800 hover:bg-forest-900 text-white rounded-full flex items-center justify-center font-bold shadow text-xs transition active:scale-95 flex-shrink-0">
              ▶
            </button>
            <div class="flex flex-col">
              <span class="text-[11px] font-extrabold text-forest-900">${r.voice_label || "Cloned Voice"}</span>
              <span class="text-[9px] text-slate-400 font-semibold">Gnani Voice Cloning</span>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Mark Taken Toggle -->
            <button onclick="toggleTaken('${r.id}')" class="px-3 py-2 rounded-xl font-bold text-xs border ${
              isTaken ? "bg-forest-800 text-white border-forest-800 shadow-sm" : "bg-white text-slate-700 border-slate-300 hover:border-forest-600"
            } transition">
              ${isTaken ? "✓ Taken" : "Mark Taken"}
            </button>

            <!-- Share WhatsApp Button -->
            <a href="${waUrl}" target="_blank" rel="noopener" class="btn-whatsapp px-3 py-2 rounded-xl font-extrabold text-xs flex items-center space-x-1.5 shadow-sm active:scale-95" title="Share reminder on WhatsApp">
              <span>💬</span>
              <span>WhatsApp</span>
            </a>
          </div>
        </div>
      </div>
    `;
    })
    .join("");
}

// Reminder audio player helper
let currentActiveAudio = null;
window.playReminderAudio = function (url, btnEl) {
  if (currentActiveAudio) {
    if (!currentActiveAudio.paused && currentActiveAudio.src.includes(url)) {
      currentActiveAudio.pause();
      btnEl.textContent = "▶";
      return;
    }
    currentActiveAudio.pause();
    currentActiveAudio = null;
  }
  const audio = new Audio(url);
  currentActiveAudio = audio;
  btnEl.textContent = "⏸";
  audio.play();
  audio.onended = () => (btnEl.textContent = "▶");
  audio.onerror = () => {
    btnEl.textContent = "▶";
    showToast("Audio playback error.", "error");
  };
};

window.toggleTaken = async function (reminderId) {
  try {
    const resp = await fetch(`/api/reminders/${reminderId}/toggle`, { method: "POST" });
    if (!resp.ok) throw new Error("Toggle failed");
    await loadRemindersDashboard();
    showToast("Dose status updated!", "success");
  } catch (e) {
    showToast("Error updating dose: " + e.message, "error");
  }
};

// ==========================================
// Utilities
// ==========================================
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}


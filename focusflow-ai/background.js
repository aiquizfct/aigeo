import { db } from './firebase-config.js';
import { doc, getDoc, setDoc, updateDoc } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

// --- QUẢN LÝ TRẠNG THÁI TIMER ---
let timerState = {
    timeLeft: 25 * 60, // 25 minutes
    isRunning: false,
    intervalId: null,
    isWorkSession: true
};

// --- KẾT NỐI VỚI AI ---
async function getApiKey() {
    const docRef = doc(db, "settings", "config");
    const docSnap = await getDoc(docRef);
    if (docSnap.exists() && docSnap.data().openRouterApiKey) {
        return docSnap.data().openRouterApiKey;
    }
    console.error("API Key not found in Firebase.");
    return null;
}

async function callOpenRouterAI(prompt) {
    const apiKey = await getApiKey();
    if (!apiKey) {
        return "Bạn đã làm rất tốt! (Lỗi: Thiếu API Key)";
    }
    try {
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: { "Authorization": `Bearer ${apiKey}`, "Content-Type": "application/json" },
            body: JSON.stringify({
                "model": "deepseek/deepseek-coder",
                "messages": [
                    { "role": "system", "content": "You are a friendly and encouraging study assistant. Keep messages concise (1-2 sentences) and positive. Respond in Vietnamese." },
                    { "role": "user", "content": prompt }
                ]
            })
        });
        if (!response.ok) {
            throw new Error(`API call failed with status: ${response.status}`);
        }
        const data = await response.json();
        return data.choices[0].message.content;
    } catch (error) {
        console.error("Lỗi khi gọi OpenRouter API:", error);
        return "Cố gắng lên, bạn đang làm rất tốt! (Lỗi API)";
    }
}

// --- LOGIC POMODORO ---
function startTimer() {
    if (timerState.isRunning) return;
    timerState.isRunning = true;
    timerState.intervalId = setInterval(() => {
        timerState.timeLeft--;
        if (timerState.timeLeft < 0) {
            clearInterval(timerState.intervalId);
            timerState.isRunning = false;
            handleSessionEnd();
        }
    }, 1000);
}

function pauseTimer() {
    clearInterval(timerState.intervalId);
    timerState.isRunning = false;
}

function resetTimer() {
    pauseTimer();
    timerState.timeLeft = 25 * 60;
    timerState.isWorkSession = true;
}

async function handleSessionEnd() {
    const isWork = timerState.isWorkSession;
    timerState.isWorkSession = !isWork;
    
    let title = isWork ? "Hết giờ làm việc!" : "Hết giờ nghỉ!";
    let prompt = isWork 
        ? "Tôi vừa hoàn thành một phiên làm việc 25 phút. Hãy khen ngợi tôi."
        : "Đã hết giờ nghỉ, hãy nhắc tôi quay lại làm việc.";
        
    timerState.timeLeft = isWork ? 5 * 60 : 25 * 60;
    
    const message = await callOpenRouterAI(prompt);
    chrome.notifications.create({
        type: 'basic',
        title: title,
        message: message,
        priority: 2
    });
}

// --- CONTEXT MENU CHO TRỢ LÝ NGHIÊN CỨU ---
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "focusflow-parent", title: "FocusFlow AI", contexts: ["selection"]
  });
  chrome.contextMenus.create({
    id: "summarize-short", title: "Tóm tắt (Ngắn)", parentId: "focusflow-parent", contexts: ["selection"]
  });
  chrome.contextMenus.create({
    id: "eli5", title: "Giải thích đơn giản", parentId: "focusflow-parent", contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    let prompt = "";
    if (info.menuItemId === "summarize-short") {
        prompt = `Tóm tắt đoạn văn sau trong 1-2 câu: "${info.selectionText}"`;
    } else if (info.menuItemId === "eli5") {
        prompt = `Giải thích thuật ngữ sau như cho một đứa trẻ 5 tuổi: "${info.selectionText}"`;
    }
    
    if (prompt && tab) {
        const result = await callOpenRouterAI(prompt);
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (text) => { alert("FocusFlow AI:\n\n" + text); },
            args: [result]
        });
    }
});


// --- LẮNG NGHE LỆNH TỪ POPUP & CONTENT SCRIPTS ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    switch (request.command) {
        case 'getTimerState':
            sendResponse(timerState);
            break;
        case 'toggleTimer':
            timerState.isRunning ? pauseTimer() : startTimer();
            sendResponse(timerState);
            break;
        case 'resetTimer':
            resetTimer();
            sendResponse(timerState);
            break;
        case 'taskCompleted':
            callOpenRouterAI(`Tôi vừa hoàn thành công việc "${request.title}". Hãy động viên tôi.`).then(message => {
                 chrome.notifications.create({
                    type: 'basic', title: "Hoàn thành công việc!", message: message, priority: 2
                });
            });
            break;
        case 'decomposeTask':
            const prompt = `Bạn là chuyên gia lập kế hoạch. Chia nhỏ công việc sau thành các bước con cụ thể: "${request.title}". Trả về một mảng JSON các chuỗi (string). Ví dụ: ["Bước 1", "Bước 2"]. Chỉ trả về mảng JSON, không có văn bản giải thích nào khác.`;
            callOpenRouterAI(prompt).then(response => {
                try {
                    const jsonMatch = response.match(/\[.*\]/s);
                    if (jsonMatch) {
                        sendResponse(JSON.parse(jsonMatch[0]));
                    } else {
                        throw new Error("AI did not return a valid JSON array.");
                    }
                } catch (e) {
                    console.error(e);
                    sendResponse({error: "Không thể phân tích phản hồi từ AI."});
                }
            });
            return true; // Báo hiệu sendResponse sẽ được gọi bất đồng bộ
        case 'toggleSidebar':
            if (sender.tab) {
                chrome.tabs.sendMessage(sender.tab.id, { command: "toggleSidebar" });
            } else if (request.tab) {
                 chrome.tabs.sendMessage(request.tab.id, { command: "toggleSidebar" });
            }
            break;
    }
    return true; // Giữ kênh message mở cho các phản hồi bất đồng bộ
});
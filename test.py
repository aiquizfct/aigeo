import os

# --- Tên thư mục dự án ---
PROJECT_NAME = "focusflow-ai"

# --- Nội dung cho từng file ---

# 1. manifest.json
manifest_content = r"""
{
  "manifest_version": 3,
  "name": "FocusFlow AI 2.0 (No Icons)",
  "version": "2.1",
  "description": "Trợ lý học tập AI giúp bạn tập trung và hiệu quả hơn.",
  "permissions": [
    "storage",
    "notifications",
    "activeTab",
    "scripting",
    "contextMenus",
    "alarms",
    "tabs"
  ],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "action": {
    "default_popup": "popup.html",
    "default_title": "FocusFlow AI"
  },
  "options_page": "admin.html",
  "content_scripts": [
    {
      "matches": [
        "<all_urls>"
      ],
      "js": [
        "content.js"
      ],
      "css": [
        "sidebar.css"
      ]
    }
  ],
  "web_accessible_resources": [
    {
      "resources": [
        "sidebar.html"
      ],
      "matches": [
        "<all_urls>"
      ]
    }
  ]
}
"""

# 2. key.js
key_js_content = r"""
// QUAN TRỌNG: Thay thế các giá trị dưới đây bằng thông tin Firebase của bạn.
// Đây là nơi duy nhất bạn cần thay đổi key.
export const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};
"""

# 3. firebase-config.js
firebase_config_js_content = r"""
// Import cấu hình từ file key.js
import { firebaseConfig } from './key.js';

// Import các hàm cần thiết từ SDK
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

// Khởi tạo Firebase
const app = initializeApp(firebaseConfig);

// Export đối tượng Firestore để các file khác có thể sử dụng
export const db = getFirestore(app);
"""

# 4. popup.html
popup_html_content = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>FocusFlow AI</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            width: 320px; 
            padding: 15px;
            background-color: #f9f9f9;
        }
        h1 { 
            font-size: 20px; 
            text-align: center; 
            margin: 0 0 15px 0;
            color: #333;
        }
        #timer { 
            font-size: 48px; 
            text-align: center; 
            margin-bottom: 15px;
            font-weight: 600;
            color: #007bff;
        }
        #controls { 
            text-align: center; 
            margin-bottom: 20px; 
            display: flex; 
            justify-content: center; 
            gap: 10px; 
        }
        button {
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.2s, transform 0.1s;
        }
        button:active {
            transform: scale(0.98);
        }
        #start-btn {
            background-color: #28a745;
            color: white;
        }
        #reset-btn {
            background-color: #6c757d;
            color: white;
        }
        #task-container { 
            display: flex; 
            gap: 5px; 
            margin-bottom: 10px; 
        }
        #task-input { 
            flex-grow: 1; 
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        #add-task-btn, #decompose-task-btn {
            background-color: #007bff;
            color: white;
            min-width: 60px;
        }
        #task-list { 
            list-style: none; 
            padding: 0; 
            margin-top: 10px; 
            max-height: 150px; 
            overflow-y: auto;
            background-color: #fff;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }
        #task-list li { 
            display: flex; 
            align-items: center; 
            padding: 8px; 
            border-bottom: 1px solid #eee; 
        }
        #task-list li:last-child {
            border-bottom: none;
        }
        #task-list li span { 
            flex-grow: 1; 
            margin: 0 8px; 
        }
        #task-list li.completed span { 
            text-decoration: line-through; 
            color: #888; 
        }
        #footer-controls { 
            margin-top: 15px; 
            text-align: center;
        }
         #toggle-sidebar-btn {
            width: 100%;
            background-color: #17a2b8;
            color: white;
            padding: 10px;
         }
    </style>
</head>
<body>
    <h1>FocusFlow AI</h1>
    <div id="timer">25:00</div>
    <div id="controls">
        <button id="start-btn">Bắt đầu</button>
        <button id="reset-btn">Reset</button>
    </div>

    <div id="task-container">
        <input type="text" id="task-input" placeholder="Thêm công việc...">
        <button id="add-task-btn">Thêm</button>
        <button id="decompose-task-btn">Phân Rã</button>
    </div>
    <ul id="task-list"></ul>
    
    <div id="footer-controls">
        <button id="toggle-sidebar-btn">Mở Trợ Lý Nghiên Cứu</button>
    </div>

    <script type="module" src="popup.js"></script>
</body>
</html>
"""

# 5. popup.js
popup_js_content = r"""
import { db } from './firebase-config.js';
import { collection, addDoc, getDocs, doc, updateDoc, deleteDoc, query, orderBy } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const timerDisplay = document.getElementById('timer');
const startBtn = document.getElementById('start-btn');
const resetBtn = document.getElementById('reset-btn');
const taskInput = document.getElementById('task-input');
const taskList = document.getElementById('task-list');
const addTaskBtn = document.getElementById('add-task-btn');
const decomposeBtn = document.getElementById('decompose-task-btn');
const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');

// --- QUẢN LÝ POMODORO TIMER ---
function updateTimerDisplay(timeLeft, isRunning) {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    startBtn.textContent = isRunning ? 'Tạm dừng' : 'Bắt đầu';
}

startBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ command: 'toggleTimer' });
});

resetBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ command: 'resetTimer' });
});

// Cập nhật UI timer mỗi giây từ background
setInterval(() => {
    chrome.runtime.sendMessage({ command: 'getTimerState' }, (response) => {
        if (response) {
            updateTimerDisplay(response.timeLeft, response.isRunning);
        }
    });
}, 1000);


// --- QUẢN LÝ CÔNG VIỆC (TASK) ---
async function renderTasks() {
    taskList.innerHTML = '';
    const q = query(collection(db, "tasks"), orderBy("createdAt", "desc"));
    const querySnapshot = await getDocs(q);
    querySnapshot.forEach((doc) => {
        createTaskElement(doc.id, doc.data());
    });
}

function createTaskElement(id, taskData) {
    const li = document.createElement('li');
    li.dataset.id = id;
    if (taskData.completed) {
        li.classList.add('completed');
    }

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = taskData.completed;
    checkbox.addEventListener('change', () => toggleTask(id, !taskData.completed, taskData.title));

    const span = document.createElement('span');
    span.textContent = taskData.title;

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Xóa';
    deleteBtn.addEventListener('click', () => deleteTask(id));

    li.appendChild(checkbox);
    li.appendChild(span);
    li.appendChild(deleteBtn);
    taskList.appendChild(li);
}

async function addTask(title) {
    if (!title || !title.trim()) return;
    await addDoc(collection(db, "tasks"), {
        title: title.trim(),
        completed: false,
        createdAt: new Date()
    });
    taskInput.value = '';
    renderTasks();
}

async function toggleTask(id, completed, title) {
    const taskRef = doc(db, "tasks", id);
    await updateDoc(taskRef, { completed });
    renderTasks();
    if (completed) {
        chrome.runtime.sendMessage({ command: 'taskCompleted', title: title });
    }
}

async function deleteTask(id) {
    await deleteDoc(doc(db, "tasks", id));
    renderTasks();
}

addTaskBtn.addEventListener('click', () => addTask(taskInput.value));
taskInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTask(e.target.value);
    }
});

// --- PHÂN RÃ CÔNG VIỆC AI ---
decomposeBtn.addEventListener('click', () => {
    const title = taskInput.value;
    if (!title || !title.trim()) {
        alert("Vui lòng nhập một công việc lớn để phân rã.");
        return;
    }
    decomposeBtn.textContent = "Đang...";
    decomposeBtn.disabled = true;
    chrome.runtime.sendMessage({ command: 'decomposeTask', title: title }, (subtasks) => {
        if (subtasks && !subtasks.error) {
            subtasks.forEach(subtask => addTask(subtask));
            taskInput.value = ''; // Xóa input sau khi phân rã
        } else {
            alert("Không thể phân rã công việc. Vui lòng thử lại.");
        }
        decomposeBtn.textContent = "Phân Rã";
        decomposeBtn.disabled = false;
    });
});

// --- MỞ/ĐÓNG SIDEBAR ---
toggleSidebarBtn.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.runtime.sendMessage({ command: 'toggleSidebar', tab: tabs[0] });
        }
    });
});


// Tải công việc và trạng thái timer khi popup mở
document.addEventListener('DOMContentLoaded', () => {
    renderTasks();
    chrome.runtime.sendMessage({ command: 'getTimerState' }, (response) => {
        if (response) {
            updateTimerDisplay(response.timeLeft, response.isRunning);
        }
    });
});
"""

# 6. background.js
background_js_content = r"""
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
"""

# 7. admin.html
admin_html_content = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Admin - FocusFlow AI</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f0f2f5;
            color: #333;
            padding: 20px;
            max-width: 900px;
            margin: 40px auto;
        }
        .container {
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        h1, h2 {
            color: #1c1e21;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
            margin-top: 0;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }
        input[type="password"], input[type="text"] {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 6px;
            box-sizing: border-box;
        }
        button {
            padding: 12px 20px;
            cursor: pointer;
            border: none;
            border-radius: 6px;
            background-color: #007bff;
            color: white;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #0056b3;
        }
        #status {
            margin-top: 15px;
            font-weight: bold;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        #status.success {
            background-color: #d4edda;
            color: #155724;
            display: block;
        }
        #status.error {
            background-color: #f8d7da;
            color: #721c24;
            display: block;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .loading {
            text-align: center;
            padding: 20px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Bảng điều khiển Admin - FocusFlow AI</h1>

    <div class="container">
        <h2>Cài đặt API Key</h2>
        <label for="apiKey">OpenRouter API Key:</label>
        <input type="password" id="apiKey" placeholder="Nhập API Key của bạn...">
        
        <button id="saveButton">Lưu Cài Đặt</button>
        <div id="status"></div>
    </div>
    
    <div class="container">
        <h2>Theo dõi Công việc (Tasks)</h2>
        <table>
            <thead>
                <tr>
                    <th>Tiêu đề</th>
                    <th>Trạng thái</th>
                    <th>Ngày tạo</th>
                </tr>
            </thead>
            <tbody id="task-table-body">
                <!-- Dữ liệu sẽ được load ở đây -->
            </tbody>
        </table>
    </div>

    <script type="module" src="admin.js"></script>
</body>
</html>
"""

# 8. admin.js
admin_js_content = r"""
import { db } from './firebase-config.js';
import { doc, setDoc, getDoc, collection, getDocs, query, orderBy } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const apiKeyInput = document.getElementById('apiKey');
const saveButton = document.getElementById('saveButton');
const statusDiv = document.getElementById('status');
const taskTableBody = document.getElementById('task-table-body');

// --- QUẢN LÝ API KEY ---
async function loadSettings() {
    try {
        const docRef = doc(db, "settings", "config");
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
            apiKeyInput.value = docSnap.data().openRouterApiKey || '';
        }
    } catch (error) {
        updateStatus("Lỗi khi tải cài đặt: " + error.message, "error");
    }
}

async function saveSettings() {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        updateStatus("Vui lòng nhập API Key.", "error");
        return;
    }
    try {
        await setDoc(doc(db, "settings", "config"), { openRouterApiKey: apiKey });
        updateStatus("Lưu API Key thành công!", "success");
    } catch (error) {
        updateStatus("Lỗi khi lưu: " + error.message, "error");
    }
}

function updateStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = type;
}

// --- THEO DÕI CÔNG VIỆC ---
async function loadTasks() {
    try {
        taskTableBody.innerHTML = '<tr><td colspan="3" class="loading">Đang tải dữ liệu công việc...</td></tr>';
        const q = query(collection(db, "tasks"), orderBy("createdAt", "desc"));
        const querySnapshot = await getDocs(q);
        
        taskTableBody.innerHTML = '';
        if (querySnapshot.empty) {
            taskTableBody.innerHTML = '<tr><td colspan="3" class="loading">Chưa có công việc nào.</td></tr>';
            return;
        }

        querySnapshot.forEach((taskDoc) => {
            const taskData = taskDoc.data();
            const row = taskTableBody.insertRow();
            
            row.insertCell(0).textContent = taskData.title;
            row.insertCell(1).textContent = taskData.completed ? 'Hoàn thành' : 'Chưa xong';
            row.insertCell(2).textContent = taskData.createdAt.toDate().toLocaleString('vi-VN');
        });
    } catch (error) {
        console.error("Lỗi khi tải công việc:", error);
        taskTableBody.innerHTML = '<tr><td colspan="3" class="loading">Không thể tải dữ liệu. Vui lòng kiểm tra cài đặt Firebase.</td></tr>';
    }
}

// Gán sự kiện và tải dữ liệu
saveButton.addEventListener('click', saveSettings);
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadTasks();
});
"""

# 9. sidebar.html
sidebar_html_content = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
</head>
<body>
    <div id="ff-sidebar-header">
        <h3>Trợ lý Nghiên cứu AI</h3>
        <button id="ff-close-btn">Đóng</button>
    </div>
    <div id="ff-chat-container">
        <div class="ff-chat-message ai">Xin chào! Tôi có thể giúp gì với nội dung trang này?</div>
    </div>
    <div id="ff-sidebar-footer">
        <textarea id="ff-chat-input" placeholder="Hỏi AI về nội dung trang..."></textarea>
        <button id="ff-send-btn">Gửi</button>
    </div>
</body>
</html>
"""

# 10. sidebar.css
sidebar_css_content = r"""
#ff-sidebar-iframe {
    position: fixed;
    top: 0;
    right: 0;
    width: 350px;
    height: 100%;
    border: none;
    z-index: 9999999;
    box-shadow: -2px 0 10px rgba(0,0,0,0.15);
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out;
}

#ff-sidebar-iframe.visible {
    transform: translateX(0);
}

/* Style for elements inside the iframe */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0;
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f9f9f9;
}

#ff-sidebar-header {
    padding: 10px 15px;
    background-color: #f1f1f1;
    border-bottom: 1px solid #ccc;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

#ff-sidebar-header h3 {
    margin: 0;
    font-size: 16px;
}

#ff-sidebar-header button {
    background: none;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
}

#ff-chat-container {
    flex-grow: 1;
    padding: 15px;
    overflow-y: auto;
}
.ff-chat-message {
    padding: 8px 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    max-width: 80%;
    word-wrap: break-word;
}
.ff-chat-message.ai {
    background-color: #e9e9eb;
    align-self: flex-start;
}
.ff-chat-message.user {
    background-color: #007bff;
    color: white;
    align-self: flex-end;
    margin-left: auto;
}

#ff-sidebar-footer {
    padding: 10px;
    border-top: 1px solid #ccc;
    display: flex;
    gap: 10px;
}

#ff-chat-input {
    flex-grow: 1;
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 8px;
    resize: none;
}
#ff-send-btn {
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 6px;
    padding: 0 15px;
    cursor: pointer;
}
"""

# 11. content.js
content_js_content = r"""
let sidebarFrame = null;

function toggleSidebar() {
    if (!sidebarFrame) {
        sidebarFrame = document.createElement('iframe');
        sidebarFrame.id = 'ff-sidebar-iframe';
        sidebarFrame.src = chrome.runtime.getURL('sidebar.html');
        document.body.appendChild(sidebarFrame);
        
        setTimeout(() => {
            sidebarFrame.classList.add('visible');
        }, 10);

    } else {
        sidebarFrame.classList.toggle('visible');
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.command === "toggleSidebar") {
        toggleSidebar();
        sendResponse({status: "done"});
    }
    return true;
});
"""

# --- Dictionary để map tên file và nội dung ---
files_to_create = {
    "manifest.json": manifest_content,
    "key.js": key_js_content,
    "firebase-config.js": firebase_config_js_content,
    "popup.html": popup_html_content,
    "popup.js": popup_js_content,
    "background.js": background_js_content,
    "admin.html": admin_html_content,
    "admin.js": admin_js_content,
    "sidebar.html": sidebar_html_content,
    "sidebar.css": sidebar_css_content,
    "content.js": content_js_content,
}

# --- Hàm chính để tạo dự án ---
def create_project():
    """Tạo thư mục và các file cho dự án FocusFlow AI."""
    print(f"Bắt đầu tạo cấu trúc dự án trong thư mục '{PROJECT_NAME}'...")

    # Tạo thư mục chính, không báo lỗi nếu đã tồn tại
    os.makedirs(PROJECT_NAME, exist_ok=True)
    print(f"Thư mục '{PROJECT_NAME}' đã sẵn sàng.")

    # Vòng lặp để tạo từng file
    for filename, content in files_to_create.items():
        file_path = os.path.join(PROJECT_NAME, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  - Đã tạo file: {file_path}")
        except IOError as e:
            print(f"  - LỖI khi tạo file {file_path}: {e}")
    
    print("\nHoàn tất! Cấu trúc dự án đã được tạo thành công.")
    print("--------------------------------------------------")
    print("Bước tiếp theo:")
    print(f"1. Mở file '{os.path.join(PROJECT_NAME, 'key.js')}'")
    print("2. Điền thông tin cấu hình Firebase của bạn vào đó.")
    print("3. Tải thư mục 'focusflow-ai' lên Chrome Extension.")

if __name__ == "__main__":
    create_project()

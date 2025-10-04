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
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
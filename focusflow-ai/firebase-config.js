// Import cấu hình từ file key.js
import { firebaseConfig } from './key.js';

// Import các hàm cần thiết từ SDK
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

// Khởi tạo Firebase
const app = initializeApp(firebaseConfig);

// Export đối tượng Firestore để các file khác có thể sử dụng
export const db = getFirestore(app);
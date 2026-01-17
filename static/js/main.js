import { initializeApp } from "https://www.gstatic.com/firebasejs/12.8.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/12.8.0/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyBTEJdQuolqA_yYQBB1ZVLNKJ39KhM1I7o",
    authDomain: "gg-login-526fa.firebaseapp.com",
    projectId: "gg-login-526fa",
    storageBucket: "gg-login-526fa.firebasestorage.app",
    messagingSenderId: "294580077426",
    appId: "1:294580077426:web:8db9d39b71916cafced3eb",
    measurementId: "G-P1CT3D01EF"
    };

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
auth.languageCode = 'vi'; // Đổi sang tiếng Việt
const provider = new GoogleAuthProvider();

const googleLogin = document.getElementById("google-login-btn");
if (googleLogin) {
    googleLogin.addEventListener("click", function () {
        signInWithPopup(auth, provider)
            .then((result) => {
                const user = result.user;
                // Send user info to backend
                fetch('/google_login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'email': user.email,
                        'name': user.displayName,
                        'avatar': user.photoURL
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = "/home";
                        } else {
                            alert(data.message || "Login failed");
                        }
                    })
                    .catch(err => {
                        console.error("Error sending data to backend:", err);
                        alert("An error occurred during login.");
                    });

            }).catch((error) => {
                console.error("Firebase Auth Error:", error);
                const errorCode = error.code;
                const errorMessage = error.message;
                alert(errorMessage);
            });
    });
}
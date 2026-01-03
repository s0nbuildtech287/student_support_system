// placeholder JS
console.log("Workout app loaded");
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";
const firebaseConfig = {
    apiKey: "AIzaSyCgEQLwL7Ky8yUB26tCbzXuCK0vLJczUZA",
    authDomain: "login-14735.firebaseapp.com",
    projectId: "login-14735",
    storageBucket: "login-14735.firebasestorage.app",
    messagingSenderId: "655978164276",
    appId: "1:655978164276:web:e35f54550dc9a0d3d91a61"
};


const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
auth.languageCode = 'en'
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
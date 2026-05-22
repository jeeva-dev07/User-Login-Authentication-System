document.addEventListener("DOMContentLoaded", () => {
    // --- 1. REGISTRATION LOGIC ---
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Updated to match the new HTML IDs perfectly!
            const username = document.getElementById("regUser").value.trim();
            const email = document.getElementById("regEmail").value.trim();
            const password = document.getElementById("regPass").value;
            const confirmPassword = document.getElementById("regConfirmPass").value;
            const errorMessageElement = document.getElementById("regError");

            if (password !== confirmPassword) {
                showError(errorMessageElement, "Passwords do not match!");
                return;
            }

            try {
                const response = await fetch("/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    alert("Registration Successful! Redirecting to login page...");
                    window.location.href = "login.html";
                } else {
                    showError(errorMessageElement, data.error || "Registration failed.");
                }
            } catch (error) {
                console.error("Fetch Error:", error);
                showError(errorMessageElement, "Connection error. Cannot reach the server.");
            }
        });
    }

    // --- 2. LOGIN LOGIC ---
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Updated to match the new Login HTML IDs perfectly!
            const username = document.getElementById("loginUser").value.trim();
            const password = document.getElementById("loginPass").value;
            const errorMessageElement = document.getElementById("loginError");

            try {
                const response = await fetch("/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    alert("Login Successful! Welcome to Dashboard.");
                    window.location.href = "dashboard.html";
                } else {
                    showError(errorMessageElement, data.error || "Invalid credentials.");
                }
            } catch (error) {
                console.error("Fetch Error:", error);
                showError(errorMessageElement, "Connection error. Cannot reach the server.");
            }
        });
    }

    // --- 3. DASHBOARD LOADER LOGIC ---
    const welcomeMsg = document.getElementById("welcomeMsg");
    if (welcomeMsg) {
        async function loadDashboardData() {
            try {
                const response = await fetch("/dashboard-data", { method: "GET" });
                
                if (response.status === 401) {
                    window.location.href = "login.html";
                    return;
                }

                const data = await response.json();
                
                document.getElementById("welcomeMsg").innerText = `Welcome, ${data.username}!`;
                document.getElementById("dashEmail").innerText = data.email;
                document.getElementById("dashRole").innerText = data.role;
                document.getElementById("dashJoinDate").innerText = data.join_date;

                const adminPanel = document.getElementById("adminPanel");
                if (data.role === "admin" && adminPanel) {
                    adminPanel.style.display = "block";
                    const userList = document.getElementById("userList");
                    if (userList && data.all_users) {
                        userList.innerHTML = ""; 
                        data.all_users.forEach(user => {
                            const li = `<li>
                                <strong>${user.username}</strong> 
                                <span class="email">(${user.email})</span>
                                <span class="badge">${user.role}</span>
                            </li>`;
                            userList.innerHTML += li;
                        });
                    }
                }
            } catch (error) {
                console.error("Dashboard Fetch Error:", error);
            }
        }
        loadDashboardData();
    }

    // --- 4. LOGOUT ACTION LOGIC ---
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            try {
                const response = await fetch("/logout", { method: "GET" });
                if (response.ok) {
                    alert("Logged out safely.");
                    window.location.href = "login.html";
                }
            } catch (error) {
                console.error("Logout Error:", error);
            }
        });
    }

    function showError(element, message) {
        if (element) {
            element.innerText = message;
            element.style.display = "block";
        } else {
            alert(message);
        }
    }
});

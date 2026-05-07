document.addEventListener("DOMContentLoaded", () => {

    const menuItems = document.querySelectorAll(".sidebar ul li");
    const sections = document.querySelectorAll("main section");
    const tbody = document.querySelector("#employee-table tbody");

    // ==========================
    // FETCH USERS FROM BACKEND
    // ==========================
    async function loadUsers(role = "all") {

        let url = "http://127.0.0.1:8000/users";

        if (role === "mentor") {
            url = "http://127.0.0.1:8000/mentors";
        } 
        else if (role === "mentee") {
            url = "http://127.0.0.1:8000/mentees";
        }

        try {
            const res = await fetch(url);
            const data = await res.json();

            tbody.innerHTML = "";

            data.forEach(user => {
                tbody.innerHTML += `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.dep}</td>
                    <td>${user.role}</td>
                    <td>${user.email}</td>
                    <td>${user.phone || "-"}</td>
                    <td><span class="status active">Active</span></td>
                    <td><button class="btn btn-danger">Delete</button></td>
                </tr>`;
            });

        } catch (err) {
            console.error("Error:", err);
        }
    }

    // ==========================
    // SIDEBAR CLICK
    // ==========================
    menuItems.forEach(item => {
        item.addEventListener("click", () => {

       menuItems.forEach(item => {
    item.addEventListener("click", () => {

        // remove active
        menuItems.forEach(i => i.classList.remove("active"));
        document.querySelectorAll(".section").forEach(sec => sec.classList.remove("active"));

        item.classList.add("active");

        const section = item.getAttribute("data-section");
        const role = item.getAttribute("data-role");

        // 👉 HIDE USER TABLE BY DEFAULT
        const userSection = document.getElementById("user-section");
        userSection.classList.remove("active");

        // 👉 SHOW CORRECT SECTION
        const target = document.getElementById(section + "-section");
        if (target) target.classList.add("active");

        // 👉 ONLY SHOW TABLE FOR MENTOR / MENTEE
      if (role === "mentor" || role === "mentee" || role === "Department")  {
            userSection.classList.add("active");

            if (role === "mentor") {
                loadUsers("mentor");
            } else if(role === "mentee") {
                loadUsers("mentee");
            }
            else{
                  loadUsers("All");
            }
        }

        // logout
        if (section === "logout") {
            window.location.href = "login.html";
        }
    });
   }); 
   });
    });

    // ==========================
    // INITIAL LOAD
    // ==========================
   // 🔥 AUTO REFRESH EVERY TIME PAGE OPENS
window.onload = () => {
    loadUsers("all");
};
});
async function loadQuestions() {
    let res = await fetch("http://127.0.0.1:8000/feedback/questions");
    let data = await res.json();

    const list = document.getElementById("question-list");
    list.innerHTML = "";

    data.forEach(q => {
        list.innerHTML += `
            <div class="question-item">
                <b>${q.question}</b> (${q.type})
            </div>
        `;
    });
}
async function addQuestion() {
    const question = document.getElementById("new-question").value;
    const type = document.getElementById("question-type").value;

    if (!question) {
        alert("Enter question");
        return;
    }

    await fetch("http://127.0.0.1:8000/feedback/add-question", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question,
            type: type
        })
    });

    document.getElementById("new-question").value = "";
    loadQuestions();
}
async function releaseFeedback() {
    await fetch("http://127.0.0.1:8000/admin/feedback/release", {
        method: "POST"
    });

    alert("✅ Feedback Released to Mentees");
}
document.addEventListener("DOMContentLoaded", () => {
    loadQuestions();
});
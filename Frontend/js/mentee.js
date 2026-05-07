document.addEventListener("DOMContentLoaded", () => {

    const menuItems = document.querySelectorAll(".sidebar ul li");
    const sections = document.querySelectorAll("main section");
    const tbody = document.querySelector("#task-table tbody");

    // ==========================
    // LOAD TASKS
    // ==========================
    async function loadTasks() {
        const url = "http://127.0.0.1:8000/tasks";

        try {
            const res = await fetch(url);

            if (!res.ok) throw new Error("Failed to fetch tasks");

            const data = await res.json();

            tbody.innerHTML = "";

            let total = data.length;
            let completed = 0;
            let pending = 0;

            data.forEach(task => {
                if (task.status === "Completed") completed++;
                else pending++;

                tbody.innerHTML += `
                <tr>
                    <td>${task.title}</td>
                    <td>${task.status}</td>
                    <td>${task.deadline}</td>
                    <td>
                        <button onclick="markComplete(${task.id})">Done</button>
                    </td>
                </tr>`;
            });

            // Update dashboard
            document.getElementById("total-tasks").innerText = total;
            document.getElementById("completed-tasks").innerText = completed;
            document.getElementById("pending-tasks").innerText = pending;

            let performance = total ? Math.round((completed / total) * 100) : 0;
            document.getElementById("performance").innerText = performance + "%";

        } catch (err) {
            console.error(err);
        }
    }

    // ==========================
    // SIDEBAR NAVIGATION
    // ==========================
    menuItems.forEach(item => {
        item.addEventListener("click", () => {

            menuItems.forEach(i => i.classList.remove("active"));
            sections.forEach(sec => sec.classList.remove("active"));

            item.classList.add("active");

            const section = item.getAttribute("data-section");

            if (section === "logout") {
                localStorage.clear();
                window.location.href = "login.html";
                return;
            }

            const target = document.getElementById(section + "-section");
            if (target) target.classList.add("active");

            if (section === "tasks") {
                loadTasks();
            }
        });
    });

    // ==========================
    // MARK COMPLETE
    // ==========================
    window.markComplete = async function(id) {
        await fetch(`http://127.0.0.1:8000/tasks/${id}`, {
            method: "PUT"
        });

        loadTasks();
    };

    // ==========================
    // INITIAL LOAD
    // ==========================
    loadTasks();
});
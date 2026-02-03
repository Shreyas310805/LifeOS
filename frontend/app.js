// ===============================
// CONFIG
// ===============================
const API_BASE = "http://127.0.0.1:8000";
const content = document.getElementById("content");

// ===============================
// NAVIGATION
// ===============================

function showDashboard() {
  content.innerHTML = `
    <h2>Dashboard</h2>
    <p>Welcome to LifeOS.</p>
    <p>Your daily productivity and health overview.</p>
  `;
}

function showTasks() {
  content.innerHTML = `
    <h2>Tasks</h2>

    <form id="taskForm">
      <input
        type="text"
        id="title"
        placeholder="Describe your task"
        required
      />
      <button type="submit">Add Task</button>
    </form>

    <ul id="taskList"></ul>
  `;

  document
    .getElementById("taskForm")
    .addEventListener("submit", addTask);

  loadTasks();
}

function showFitness() {
  content.innerHTML = `
    <h2>Fitness</h2>
    <p>Fitness tracking coming soon.</p>
  `;
}

function showHealth() {
  content.innerHTML = `
    <h2>Health</h2>
    <p>Medication and health insights.</p>
  `;
}

function showLeaderboard() {
  content.innerHTML = `
    <h2>Leaderboard</h2>
    <p>Competitive rankings will appear here.</p>
  `;
}

// ===============================
// TASK API
// ===============================

async function addTask(event) {
  event.preventDefault();

  const title = document.getElementById("title").value;

  try {
    await fetch(
      `${API_BASE}/tasks?title=${encodeURIComponent(title)}`,
      { method: "POST" }
    );

    document.getElementById("taskForm").reset();
    loadTasks();

  } catch (error) {
    console.error("Failed to add task:", error);
  }
}

async function loadTasks() {
  try {
    const res = await fetch(`${API_BASE}/tasks`);
    const tasks = await res.json();

    const taskList = document.getElementById("taskList");
    taskList.innerHTML = "";

    if (tasks.length === 0) {
      taskList.innerHTML = "<li>No tasks added yet.</li>";
      return;
    }

    tasks.forEach(task => {
      const li = document.createElement("li");
      li.textContent = `${task.title} (${task.difficulty}) - ${task.points} pts`;
      taskList.appendChild(li);
    });

  } catch (error) {
    console.error("Failed to load tasks:", error);
  }
}

// ===============================
// INITIAL LOAD
// ===============================

document.addEventListener("DOMContentLoaded", () => {
  showDashboard();
});

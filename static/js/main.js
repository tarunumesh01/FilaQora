/* FilaQora client helpers */
document.addEventListener("DOMContentLoaded", function () {
  // Confirm delete buttons
  document.querySelectorAll(".js-confirm-delete").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var msg = btn.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // Dashboard charts (real dashboard page)
  var dataEl = document.getElementById("dashboard-data");
  if (!dataEl) return;
  // Demo page has its own scripts block; only run if real dashboard canvases exist
  if (!document.getElementById("customersByMonth")) return;

  try {
    var data = JSON.parse(dataEl.textContent);

    var ctx1 = document.getElementById("customersByMonth");
    if (ctx1) {
      new Chart(ctx1, {
        type: "bar",
        data: {
          labels: data.month_labels || [],
          datasets: [{
            label: "New customers",
            data: data.month_counts || [],
            backgroundColor: "rgba(37, 99, 235, 0.75)",
            borderRadius: 6,
            maxBarThickness: 48
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, ticks: { precision: 0 } }
          }
        }
      });
    }

    var ctx2 = document.getElementById("topCompanies");
    if (ctx2) {
      new Chart(ctx2, {
        type: "doughnut",
        data: {
          labels: data.company_labels || [],
          datasets: [{
            data: data.company_counts || [],
            backgroundColor: ["#2563eb", "#38bdf8", "#6366f1", "#8b5cf6", "#a855f7"],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom" } },
          cutout: "55%"
        }
      });
    }

    var ctx3 = document.getElementById("tagDistribution");
    if (ctx3) {
      new Chart(ctx3, {
        type: "pie",
        data: {
          labels: data.tag_labels || [],
          datasets: [{
            data: data.tag_counts || [],
            backgroundColor: ["#22c55e", "#f59e0b", "#ef4444", "#2563eb"],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom" } }
        }
      });
    }
  } catch (err) {
    console.warn("Dashboard chart init failed", err);
  }
});

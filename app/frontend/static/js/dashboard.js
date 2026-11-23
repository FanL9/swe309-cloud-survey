// Dashboard charts (Chart.js 4). Colours come from the CSS theme variables
// so the charts always match the rating pills.
(function () {
  var el = document.getElementById("chart-data");
  if (!el || !window.Chart) return;
  var data = JSON.parse(el.textContent);
  var css = getComputedStyle(document.documentElement);
  var color = function (name) { return css.getPropertyValue(name).trim(); };
  var ratings = ["Good", "OK", "Poor"];
  var palette = { Good: color("--good"), OK: color("--ok"), Poor: color("--poor") };

  Chart.defaults.font.family = css.getPropertyValue("--bs-body-font-family");
  Chart.defaults.color = color("--text-soft");
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.pointStyle = "circle";
  Chart.defaults.plugins.legend.labels.boxWidth = 8;
  Chart.defaults.plugins.legend.labels.boxHeight = 8;

  new Chart(document.getElementById("trend-chart"), {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: ratings.map(function (r) {
        return {
          label: r,
          data: data.series[r],
          backgroundColor: palette[r],
          // White gaps between stacked segments give a cleaner, tiled look.
          borderColor: "#fff",
          borderWidth: 2,
          borderRadius: 6,
          borderSkipped: false,
          maxBarThickness: 30,
        };
      }),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { position: "top", align: "end" } },
      scales: {
        x: { stacked: true, grid: { display: false }, border: { display: false } },
        y: {
          stacked: true,
          beginAtZero: true,
          ticks: { precision: 0 },
          grid: { color: color("--line") },
          border: { display: false },
        },
      },
    },
  });

  new Chart(document.getElementById("dist-chart"), {
    type: "doughnut",
    data: {
      labels: ratings,
      datasets: [{
        data: data.distribution,
        backgroundColor: ratings.map(function (r) { return palette[r]; }),
        borderColor: "#fff",
        borderWidth: 4,
        borderRadius: 8,
        spacing: 2,
        hoverOffset: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "68%",
      plugins: { legend: { display: false } },
    },
  });
})();

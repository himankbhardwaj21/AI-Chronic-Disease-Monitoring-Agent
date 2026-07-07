/**
 * dashboard.js — ChronicCare AI Dashboard Charts & Visualizations
 * Uses Chart.js 4.x with custom healthcare theme
 */

/* ================================================================
   CHART DEFAULTS
   ================================================================ */
Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = '#64748b';
Chart.defaults.plugins.legend.labels.boxWidth = 12;
Chart.defaults.plugins.legend.labels.padding = 10;

/* Detect dark mode */
function isDark() {
  return document.documentElement.getAttribute('data-bs-theme') === 'dark';
}
function gridColor() { return isDark() ? 'rgba(255,255,255,.07)' : 'rgba(0,0,0,.06)'; }
function tickColor() { return isDark() ? '#8b949e' : '#64748b'; }

const chartInstances = {};

/* ================================================================
   SHARED CHART OPTIONS
   ================================================================ */
function lineOptions(yLabel = '') {
  return {
    responsive: true,
    maintainAspectRatio: true,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { position: 'top', align: 'end', labels: { color: tickColor() } },
      tooltip: { cornerRadius: 8, padding: 10 }
    },
    scales: {
      x: {
        grid: { color: gridColor(), drawBorder: false },
        ticks: { color: tickColor(), maxTicksLimit: 8 }
      },
      y: {
        grid: { color: gridColor(), drawBorder: false },
        ticks: { color: tickColor() },
        title: { display: !!yLabel, text: yLabel, color: tickColor(), font: { size: 10 } }
      }
    }
  };
}

/* ================================================================
   BLOOD PRESSURE CHART
   ================================================================ */
function initBPChart() {
  const ctx = document.getElementById('bpChart');
  if (!ctx || !chartData.labels?.length) return;

  chartInstances.bp = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Systolic',
          data: chartData.systolic_bp,
          borderColor: '#dc3545',
          backgroundColor: 'rgba(220,53,69,.12)',
          fill: true, tension: 0.35, pointRadius: 3, borderWidth: 2
        },
        {
          label: 'Diastolic',
          data: chartData.diastolic_bp,
          borderColor: '#fd7e14',
          backgroundColor: 'rgba(253,126,20,.08)',
          fill: false, tension: 0.35, pointRadius: 3, borderWidth: 2
        }
      ]
    },
    options: {
      ...lineOptions('mmHg'),
      plugins: {
        ...lineOptions().plugins,
        annotation: {
          annotations: {
            highLine: {
              type: 'line', yMin: 140, yMax: 140,
              borderColor: 'rgba(220,53,69,.4)', borderWidth: 1,
              borderDash: [4, 4],
              label: { content: 'High (140)', enabled: true, position: 'end', font: { size: 9 } }
            }
          }
        }
      }
    }
  });
}

/* ================================================================
   BLOOD GLUCOSE CHART
   ================================================================ */
function initGlucoseChart() {
  const ctx = document.getElementById('glucoseChart');
  if (!ctx || !chartData.labels?.length) return;

  chartInstances.glucose = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: 'Blood Glucose (mg/dL)',
        data: chartData.blood_glucose,
        borderColor: '#ffc107',
        backgroundColor: 'rgba(255,193,7,.15)',
        fill: true, tension: 0.35, pointRadius: 3, borderWidth: 2
      }]
    },
    options: lineOptions('mg/dL')
  });
}

/* ================================================================
   HEART RATE CHART
   ================================================================ */
function initHRChart() {
  const ctx = document.getElementById('hrChart');
  if (!ctx || !chartData.labels?.length) return;

  chartInstances.hr = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: 'Heart Rate',
        data: chartData.heart_rate,
        borderColor: '#e91e8c',
        backgroundColor: 'rgba(233,30,140,.10)',
        fill: true, tension: 0.35, pointRadius: 3, borderWidth: 2
      }]
    },
    options: lineOptions('bpm')
  });
}

/* ================================================================
   OXYGEN CHART
   ================================================================ */
function initO2Chart() {
  const ctx = document.getElementById('o2Chart');
  if (!ctx || !chartData.labels?.length) return;

  chartInstances.o2 = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: 'SpO₂ (%)',
        data: chartData.oxygen_saturation,
        borderColor: '#0dcaf0',
        backgroundColor: 'rgba(13,202,240,.12)',
        fill: true, tension: 0.35, pointRadius: 3, borderWidth: 2
      }]
    },
    options: {
      ...lineOptions('%'),
      scales: {
        ...lineOptions('%').scales,
        y: {
          ...lineOptions('%').scales.y,
          min: 85, max: 100
        }
      }
    }
  });
}

/* ================================================================
   HEALTH SCORE TREND CHART
   ================================================================ */
function initScoreChart() {
  const ctx = document.getElementById('scoreChart');
  if (!ctx || !chartData.labels?.length) return;

  const scores = chartData.health_scores || [];
  const colors = scores.map(s =>
    s >= 80 ? 'rgba(5,150,105,.8)' :
    s >= 60 ? 'rgba(217,119,6,.8)' :
              'rgba(220,38,38,.8)'
  );

  chartInstances.score = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: [{
        label: 'Health Score',
        data: scores,
        backgroundColor: colors,
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: {
      ...lineOptions('/100'),
      scales: {
        ...lineOptions('/100').scales,
        y: { ...lineOptions('/100').scales.y, min: 0, max: 100 }
      }
    }
  });
}

/* ================================================================
   RISK GAUGE (Doughnut)
   ================================================================ */
function initRiskGauge() {
  const ctx = document.getElementById('riskGauge');
  if (!ctx) return;

  const pct = typeof riskPct !== 'undefined' ? riskPct : 0;
  const level = typeof riskLevel !== 'undefined' ? riskLevel : 'Low';
  const colors = {
    'Low':      ['#059669', '#e2e8f0'],
    'Medium':   ['#d97706', '#fef3c7'],
    'High':     ['#dc2626', '#fee2e2'],
    'Critical': ['#7f1d1d', '#fca5a5'],
    'Unknown':  ['#94a3b8', '#f1f5f9'],
  };
  const [activeColor, bgColor] = colors[level] || colors['Unknown'];

  chartInstances.risk = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [pct, 100 - pct],
        backgroundColor: [activeColor, bgColor],
        borderWidth: 0,
        circumference: 180,
        rotation: -90,
        borderRadius: 4,
      }]
    },
    options: {
      responsive: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      cutout: '70%',
      animation: { animateRotate: true, duration: 1200 }
    }
  });
}

/* ================================================================
   HEALTH SCORE RING (Doughnut)
   ================================================================ */
function initHealthScoreRing() {
  const ctx = document.getElementById('healthScoreGauge');
  if (!ctx) return;

  const score = typeof healthScore !== 'undefined' ? healthScore : 0;
  const color = score >= 80 ? '#059669' : score >= 60 ? '#d97706' : '#dc2626';

  chartInstances.healthRing = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [color, isDark() ? '#30363d' : '#f1f5f9'],
        borderWidth: 0, borderRadius: 6
      }]
    },
    options: {
      responsive: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      cutout: '72%',
      animation: { animateRotate: true, duration: 1000 }
    }
  });
}

/* ================================================================
   DARK MODE CHART UPDATE
   ================================================================ */
function updateChartsForTheme() {
  Object.values(chartInstances).forEach(chart => {
    if (!chart) return;
    chart.options.scales?.x && (chart.options.scales.x.grid.color = gridColor());
    chart.options.scales?.x && (chart.options.scales.x.ticks.color = tickColor());
    chart.options.scales?.y && (chart.options.scales.y.grid.color = gridColor());
    chart.options.scales?.y && (chart.options.scales.y.ticks.color = tickColor());
    chart.options.plugins?.legend?.labels && (chart.options.plugins.legend.labels.color = tickColor());
    chart.update('none');
  });
}

// Watch for theme changes
const themeObserver = new MutationObserver(() => updateChartsForTheme());
themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-bs-theme'] });

/* ================================================================
   INIT ALL
   ================================================================ */
document.addEventListener('DOMContentLoaded', () => {
  // Small delay to ensure DOM is ready
  setTimeout(() => {
    initBPChart();
    initGlucoseChart();
    initHRChart();
    initO2Chart();
    initScoreChart();
    initRiskGauge();
    initHealthScoreRing();
  }, 100);
});

// Statistics Charts
const chartConfig = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        font: {
          size: 13,
          weight: '600'
        }
      }
    }
  }
};

// Weekly Progress Chart
const weeklyCtx = document.getElementById('weeklyChart');
if (weeklyCtx) {
  new Chart(weeklyCtx, {
    type: 'bar',
    data: {
      labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
      datasets: [
        {
          label: 'Buổi tập',
          data: [1, 2, 1, 2, 1, 0, 1],
          backgroundColor: '#343a40',
          borderColor: '#212529',
          borderWidth: 1,
          borderRadius: 6
        }
      ]
    },
    options: chartConfig
  });
}

// Body Part Focus Chart
const bodyPartCtx = document.getElementById('bodyPartChart');
if (bodyPartCtx) {
  new Chart(bodyPartCtx, {
    type: 'doughnut',
    data: {
      labels: ['Chân', 'Lưng', 'Ngực', 'Vai', 'Tay'],
      datasets: [
        {
          data: [25, 22, 20, 18, 15],
          backgroundColor: [
            '#343a40',
            '#495057',
            '#6c757d',
            '#adb5bd',
            '#dee2e6'
          ],
          borderColor: '#fff',
          borderWidth: 2
        }
      ]
    },
    options: chartConfig
  });
}

// Monthly Trend Chart
const monthlyCtx = document.getElementById('monthlyChart');
if (monthlyCtx) {
  new Chart(monthlyCtx, {
    type: 'line',
    data: {
      labels: ['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần 4'],
      datasets: [
        {
          label: 'Buổi tập',
          data: [5, 7, 6, 8],
          borderColor: '#343a40',
          backgroundColor: 'rgba(52, 58, 64, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 6,
          pointBackgroundColor: '#343a40',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        }
      ]
    },
    options: {
      ...chartConfig,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 2
          }
        }
      }
    }
  });
}

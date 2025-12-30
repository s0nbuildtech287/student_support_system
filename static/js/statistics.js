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
          backgroundColor: '#667eea',
          borderColor: '#764ba2',
          borderWidth: 1,
          borderRadius: 6
        }
      ]
    },
    options: chartConfig
  });
}

// Favorite Subject Chart
const bodyPartCtx = document.getElementById('bodyPartChart');
if (bodyPartCtx) {
  new Chart(bodyPartCtx, {
    type: 'doughnut',
    data: {
      labels: ['Lập trình Python cơ bản', 'Cấu trúc dữ liệu & Giải thuật', 'Machine Learning cơ bản', 'Lập trình Web cơ bản', 'Cơ sở dữ liệu'],
      datasets: [
        {
          data: [25, 22, 20, 18, 15],
          backgroundColor: [
            '#667eea',
            '#764ba2',
            '#f093fb',
            '#4facfe',
            '#00f2fe'
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
          borderColor: '#764ba2',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 6,
          pointBackgroundColor: '#667eea',
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

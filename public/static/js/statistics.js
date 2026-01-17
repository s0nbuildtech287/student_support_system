// Statistics Charts - Sử dụng dữ liệu động từ server
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

// Lấy dữ liệu từ server (được truyền qua biến statsData)
const weeklyData = typeof statsData !== 'undefined' ? statsData.weekly : { labels: [], data: [] };
const favoriteData = typeof statsData !== 'undefined' ? statsData.favorite : { labels: [], data: [] };
const monthlyData = typeof statsData !== 'undefined' ? statsData.monthly : { labels: [], data: [] };

// Weekly Progress Chart - Dữ liệu từ database
const weeklyCtx = document.getElementById('weeklyChart');
if (weeklyCtx) {
  new Chart(weeklyCtx, {
    type: 'bar',
    data: {
      labels: weeklyData.labels || ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
      datasets: [
        {
          label: 'Hoạt động học tập',
          data: weeklyData.data || [0, 0, 0, 0, 0, 0, 0],
          backgroundColor: '#667eea',
          borderColor: '#764ba2',
          borderWidth: 1,
          borderRadius: 6
        }
      ]
    },
    options: {
      ...chartConfig,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  });
}

// Favorite Subject Chart - Dữ liệu từ database
const bodyPartCtx = document.getElementById('bodyPartChart');
if (bodyPartCtx) {
  new Chart(bodyPartCtx, {
    type: 'doughnut',
    data: {
      labels: favoriteData.labels || ['Chưa có dữ liệu'],
      datasets: [
        {
          data: favoriteData.data || [1],
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

// Monthly Trend Chart - Dữ liệu từ database
const monthlyCtx = document.getElementById('monthlyChart');
if (monthlyCtx) {
  new Chart(monthlyCtx, {
    type: 'line',
    data: {
      labels: monthlyData.labels || ['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần 4'],
      datasets: [
        {
          label: 'Hoạt động học tập',
          data: monthlyData.data || [0, 0, 0, 0],
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

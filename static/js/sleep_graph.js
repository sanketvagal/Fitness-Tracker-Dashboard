const labels = {{ sleep_date|map('string')|list|tojson }}
const data = {
  labels: labels,
  datasets: [{
    label: 'Sleep duration',
    backgroundColor: 'rgb(255, 99, 132)',
    borderColor: 'rgb(255, 99, 132)',
    data: {{sleep_durn}},
  }]
};
const config = {
  type: 'line',
  data,
  options: {}
};
var myChart = new Chart(
    document.getElementById('sleep_graph'),
    config
);
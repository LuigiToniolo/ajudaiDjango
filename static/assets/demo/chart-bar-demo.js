// Bar Chart Example
var ctx = document.getElementById("myBarChart");

// Parse the JSON from the Django context
console.log('{{ conversas_per_months | safe }}')
var months = JSON.parse('{{ conversas_per_months | safe }}');
console.log(months); 

var labels = months.map(function(month) {
  return month[0];
});

var data = months.map(function(month) {
  return month[1];
});

var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [{
      label: "Revenue",
      backgroundColor: "#5C7AD3",
      borderColor: "#5C7AD3",
      data: data,
    }],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'month'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 6
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 20000,
          maxTicksLimit: 5
        },
        gridLines: {
          display: true
        }
      }],
    },
    legend: {
      display: false
    }
  }
});

// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Bar Chart Example
var ctx = document.getElementById("myBarChart");

// Obter a data atual
var currentDate = new Date();

// Array para armazenar as labels
var labels = [];

// Loop para obter os seis meses anteriores, incluindo o mês atual
for (var i = 5; i >= 0; i--) {
  var date = new Date(currentDate);
  date.setMonth(date.getMonth() - i);
  labels.push(date.toLocaleDateString("pt-BR", { month: 'long' }));
}

var data = [];
for (var j = 0; j < 6; j++) {
  var randomValue = Math.floor(Math.random() * 20000);
  data.push(randomValue);
}

var myLineChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [{
      label: "Revenue",
      // backgroundColor: "rgba(2,117,216,1)",
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
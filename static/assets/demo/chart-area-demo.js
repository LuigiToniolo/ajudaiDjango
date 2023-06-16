// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

var ctx = document.getElementById("myAreaChart");

// Obter a data atual
var currentDate = new Date();

// Array para armazenar as labels
var labels = [];

// Loop para obter as datas dos últimos 30 dias
for (var i = 29; i >= 0; i--) {
  var date = new Date(currentDate);
  date.setDate(date.getDate() - i);
  labels.push(date.toLocaleDateString("pt-BR", { month: 'short', day: 'numeric' }));
}

// Gerar 30 valores aleatórios para o campo "data"
var data = [];
for (var j = 0; j < 30; j++) {
  var randomValue = Math.floor(Math.random() * 1000);
  data.push(randomValue);
}

var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: labels,
    datasets: [{
      label: "Conversas",
      lineTension: 0.3,
      backgroundColor: "rgba(2,117,216,0.2)",
      borderColor: "#5C7AD3",
      pointRadius: 5,
      pointBackgroundColor: "#5C7AD3",
      pointBorderColor: "rgba(255,255,255,0.8)",
      pointHoverRadius: 5,
      pointHoverBackgroundColor: "#5C7AD3",
      pointHitRadius: 50,
      pointBorderWidth: 2,
      data: data,
    }],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 1000,
          maxTicksLimit: 5
        },
        gridLines: {
          color: "rgba(0, 0, 0, .125)",
        }
      }],
    },
    legend: {
      display: false
    }
  }
});

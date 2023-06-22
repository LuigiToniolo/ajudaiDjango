

 // Script para fazer aparecer ou desaparecer mensagem de status de fatura -> o valor 1 é a mensagem que é para aparecer 
  //quando a fatura não for fechada e o valor 2 é pra aparecer a mensagem de fatura fechada.
//   var valor = 1; // Defina o valor desejado (1 ou 2)

//   var divFaturaAberta = document.getElementById("conteudo-fatura-aberta");
//   var divFaturaFechada = document.getElementById("conteudo-fatura-fechada");
  
//   if (valor === 1) {
//     divFaturaAberta.style.display = "block";
//     divFaturaFechada.style.display = "none";
//     divTeste.style.display = "none"
//   } else if (valor === 2) {
//     divFaturaAberta.style.display = "none";
//     divFaturaFechada.style.display = "block";
//     divTeste.style.display = "block";
//   }
  

  // Função para alternar a exibição das divs com base no valor fornecido
  function toggleDiv(valor) {
    var divFaturaAberta = document.getElementById("conteudo-fatura-aberta");
    var divFaturaFechada = document.getElementById("conteudo-fatura-fechada");
    var divFaturaFechadaPlano = document.getElementById("conteudo-fatura-fechada-plano");
  
    if (valor === 1) {
      if (divFaturaAberta) divFaturaAberta.style.display = "block";
      if (divFaturaFechada) divFaturaFechada.style.display = "none";
      if (divFaturaFechadaPlano) divFaturaFechadaPlano.style.display = "none";
    } else if (valor === 2) {
      if (divFaturaAberta) divFaturaAberta.style.display = "none";
      if (divFaturaFechada) divFaturaFechada.style.display = "block";
      if (divFaturaFechadaPlano) divFaturaFechadaPlano.style.display = "block";
    }
  }
  
  // Obter o valor desejado (1 ou 2) de alguma forma (por exemplo, uma variável do Django)
  var valorDesejado = 2; // Altere o valor aqui conforme necessário
  
  // Chamada da função para alternar a exibição das divs com base no valor fornecido
  toggleDiv(valorDesejado);
  
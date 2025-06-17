// Código JavaScript do frontend //

function login() {
    var email = document.getElementById('form1Example13').value;
    var password = document.getElementById('form1Example23').value;

    if (email && password) {
        window.location.href = '/dashboard';  // 🔹 Agora o Flask renderiza a página
    } else {
        alert('Por favor, preencha todos os campos.');
    }
}

$(function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    var toastTriggerList = [].slice.call(document.getElementsByClassName("toast"))
    toastTriggerList.forEach(element => {
        element.getElementsByClassName("toast-body")[0].innerHTML = element.getAttribute('toast-body');
        if (element.getAttribute("timeout")) {
            setTimeout(() => {
                element.classList.remove('show')
            }, element.getAttribute('timeout') * 1000);
        }
        element.onclick = function() {
            element.classList.remove('show')
        }
        if (element.getAttribute("show") == "True") {
            setTimeout(() => {
                element.classList.add('show')
            }, 100);
        }
    });
});

function toggleNav() {
    const navbarMobile = document.getElementById('navbar-mobile');
    if (navbarMobile.classList[0] === 'show') {
        navbarMobile.classList.remove('show');
    } else {
        navbarMobile.classList.add('show');
    }
}
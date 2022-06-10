$(function() {

    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    navMobile = document.getElementById('navbar-mobile')
    navs = [].slice.call(document.getElementsByClassName('menu_list'))
    navs.forEach((i) => { navMobile.appendChild(i.cloneNode(true)) })

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
    const navbarMobile = document.getElementById('sidebar');
    const navbarButton = document.getElementById('btn-open-sidebar');
    if (navbarMobile.classList[0] === 'show') {
        navbarMobile.classList.remove('show');
        navbarButton.removeAttribute('style')

    } else {
        navbarMobile.classList.add('show');
        navbarButton.setAttribute('style', 'display:none!important')

    }
}
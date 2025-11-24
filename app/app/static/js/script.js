// همبرگری موبایل
document.querySelectorAll('.navbar-toggler').forEach(t => {
    t.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('show');
    });
});

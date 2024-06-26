document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Simulate login
    if (username === 'dm' && password === 'dm123') {
        showDMMenu();
    } else if (username === 'player' && password === 'player123') {
        showPlayerDashboard();
    } else {
        alert('Invalid credentials');
    }
});

function showDMMenu() {
    document.getElementById('login').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('dashboardTitle').innerText = 'DM Dashboard';
    document.getElementById('dmMenu').style.display = 'block';
}

function showPlayerDashboard() {
    document.getElementById('login').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('dashboardTitle').innerText = 'Player Dashboard';
    document.getElementById('playerDashboard').style.display = 'block';

    // Sample data for player dashboard
    document.getElementById('health').innerText = '100';
    document.getElementById('stats').innerText = 'Strength: 15, Dexterity: 12, Constitution: 14, Intelligence: 10, Wisdom: 8, Charisma: 13';
    document.getElementById('skills').innerText = 'Acrobatics: +2, Arcana: +0, Athletics: +4, Deception: +1';
    document.getElementById('saves').innerText = 'Strength: +4, Dexterity: +1, Constitution: +2, Intelligence: +0, Wisdom: -1, Charisma: +1';
    document.getElementById('initiative').innerText = '+1';
    document.getElementById('ac').innerText = '16';
}

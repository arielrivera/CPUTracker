document.addEventListener('DOMContentLoaded', function () {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const modeSelect = document.getElementById('mode-select');
    const spinner = document.getElementById('spinner');
    const output = document.getElementById('output');

    startBtn.addEventListener('click', function () {
        const mode = modeSelect.value;
        spinner.classList.remove('hidden');
        output.innerHTML = '';

        fetch('/start_process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mode: mode })
        })
            .then(response => response.json())
            .then(data => {
                spinner.classList.add('hidden');
                output.innerHTML = data.message;
            })
            .catch(error => {
                spinner.classList.add('hidden');
                output.innerHTML = 'Error: ' + error.message;
            });
    });

    stopBtn.addEventListener('click', function () {
        fetch('/stop_process', {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                output.innerHTML = data.message;
            })
            .catch(error => {
                output.innerHTML = 'Error: ' + error.message;
            });
    });
});
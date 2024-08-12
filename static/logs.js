$(document).ready(function() {
    
    fetchAuditLogs();

});

document.getElementById('start-btn').addEventListener('click', startProcess);
document.getElementById('stop-btn').addEventListener('click', stopProcess);

function startProcess() {
    //fetchAuditLogs();
    const mode = document.getElementById('mode-select').value;
    document.getElementById('spinner').classList.remove('d-none');
    document.getElementById('output').innerHTML = '';

    fetch('/start_process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode: mode })
    }).then(response => response.json())
        .then(data => {
            document.getElementById('spinner').classList.add('d-none');
            document.getElementById('output').innerHTML = data.message;
        });
}

function stopProcess() {
    // stopFetchingLogs();
    fetch('/stop_process', {
        method: 'POST'
    }).then(response => response.json())
        .then(data => {
            document.getElementById('spinner').classList.add('d-none');
            document.getElementById('output').innerHTML += '<br>' + data.message;
            fetchAuditLogs();
        });
}

function fetchAuditLogs() {
    fetch('/read_audit?audit_type=7zlogfiles,rowcount=100')
        .then(response => response.json())
        .then(data => {
            const outputElement = document.getElementById('output');
            outputElement.innerHTML = '';
            data.forEach(record => {
                const logEntry = document.createElement('div');
                logEntry.textContent = record.message;
                outputElement.appendChild(logEntry);
            });
        });
}

// Fetch logs every 5 seconds
// setInterval(fetchAuditLogs, 5000);

// document.addEventListener('DOMContentLoaded', fetchAuditLogs);

// // Function to stop the interval
// function stopFetchingLogs() {
//     clearInterval(intervalId);
//     console.log('Stopped fetching logs.');
// }

// // Example condition to stop the interval after 1 minute
// setTimeout(stopFetchingLogs, 120000); // Stops after 120 seconds


// document.getElementById('start-btn').addEventListener('click', startProcess);
// document.getElementById('stop-btn').addEventListener('click', stopProcess);

// const startBtn = document.getElementById('start-btn');
// const stopBtn = document.getElementById('stop-btn');
// const spinner = document.getElementById('spinner');
// const output = document.getElementById('output');

// function startProcess() {
//     const mode = document.getElementById('mode-select').value;
//     document.getElementById('spinner').classList.remove('d-none');
//     document.getElementById('output').innerHTML = '';

//     fetch('/run_process_logs')
//         .then(response => response.text())
//         .then(data => {
//           document.getElementById('spinner').classList.add('d-none');
//           document.getElementById('output').innerHTML = data.message;

//           output.innerHTML += `<br>${data}`;
//           // Hide the spinner
//           spinner.classList.add('d-none');
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             output.innerHTML += `<br>Error: ${error}`;
//             // Hide the spinner
//             spinner.classList.add('d-none');
//       });

// }

// function stopProcess() {
//     console.log('Stop button clicked');
//     output.innerHTML = 'Process stopped.';
//     spinner.classList.add('d-none');

//     fetch('/stop_process', {
//         method: 'POST'
//     }).then(response => response.json())
//       .then(data => {
//           document.getElementById('spinner').classList.add('d-none');
//           document.getElementById('output').innerHTML += '<br>' + data.message;
//       });
// }




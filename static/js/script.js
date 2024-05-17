var socket = io();
var running = true;

socket.on('stream', function(data) {
    var img = document.getElementById('video');
    img.src = 'data:image/jpeg;base64,' + data.image;
});

socket.on('text', function(data) {
    var textContainer = document.getElementById('text-container');
    var newMessage = document.createElement('div');
    newMessage.classList.add('message');
    newMessage.textContent = data.message;
    textContainer.appendChild(newMessage);
    textContainer.scrollTop = textContainer.scrollHeight;
});

function toggleApp() {
    var controlButton = document.getElementById('control-button');
    if (running) {
        fetch('/stop')
            .then(response => response.json())
            .then(data => {
                console.log('App stopped:', data);
                alert('The application has been stopped.');
                controlButton.innerHTML = '<span>▶️ Resume</span>';
                running = false;
            })
            .catch((error) => {
                console.error('Error stopping the app:', error);
            });
    } else {
        fetch('/resume')
            .then(response => response.json())
            .then(data => {
                console.log('App resumed:', data);
                alert('The application has resumed.');
                controlButton.innerHTML = '<span>⏹ Stop</span>';
                running = true;
            })
            .catch((error) => {
                console.error('Error resuming the app:', error);
            });
    }
}

function setInterval() {
    var intervalInput = document.getElementById('interval-input').value;
    fetch('/set_interval', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ interval: parseInt(intervalInput) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'interval updated') {
            alert('Capture interval updated to ' + data.interval + ' seconds.');
        } else {
            alert('Failed to update interval: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error setting interval:', error);
    });
}

function submitKeys() {
    fetch('/update-keys', {
        method: 'POST',
        body: new FormData(document.getElementById('keys-form')),
    }).then(response => {
        if (response.ok) {
            document.getElementById('keys-update-notification').style.display = 'block';
        }
    });
}
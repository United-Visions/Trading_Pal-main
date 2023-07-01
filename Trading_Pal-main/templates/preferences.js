// preferences.js
function submitPreferences() {
    fetch('/update-preferences', {
        method: 'POST',
        body: new FormData(document.getElementById('preferences-form')),
    }).then(response => {
        if (response.ok) {
            document.getElementById('preferences-update-notification').style.display = 'block';
        }
    });
}

 
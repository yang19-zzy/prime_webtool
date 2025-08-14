
function showErrorPopup(msg) {
    const popupDiv = document.querySelector('#error-popup');
    console.log('showErrorPopup', msg);
    const popup = popupDiv.querySelector('p');
    popup.textContent = msg;
    popupDiv.style.display = 'flex';
}

// main
document.addEventListener("DOMContentLoaded", function () {
    // redirect login
    const loginBtn = document.getElementById("login-btn");
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            redirectToLogin();
        })
    }

    // fetch form submit response
    const form = document.querySelector("#tools-pdf-container-test form");
    const downloadLink = form.querySelector("#status-bar");
    
    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        downloadLink.innerHTML = '';
        
        const formData = new FormData(form);
        try {
            const res = await fetch(
                form.action, {method:'POST', body: formData}
            ).then(response => {
                if (!response.ok) {
                    msg = response.json();
                    showErrorPopup('Error during form submission: ' + msg.message);
                }
                return response;
            }).catch(response => {
                msg = response.json();
                console.error('Error during form submission:', response);
                showErrorPopup('Error during form submission: ' + msg.message);
            });
            console.log(res);
            if (!res.ok || formData.length === 0) {
                // popup.textContent = 'No file uploaded.';
                showErrorPopup('Warning: No file uploaded.');
                return;
            }
            const statusUrl = res.headers.get('Location');
            if (!res) {
                redirectToLogin();
                return
            }
            // if (!res.ok) throw new Error('Upload failed');
            downloadLink.href = '';
            downloadLink.removeAttribute('href');
            downloadLink.innerHTML = 'Processing';
            const data = await res.json();
            const jobId = data.job_id;
            const effectiveStatusUrl = statusUrl || `/tools/check-status/${jobId}`;

            const interval = setInterval(async () => {
                const statusRes = await fetch(effectiveStatusUrl, { cache: 'no-cache' });
                const statusData = await statusRes.json();
                if (statusData.status === 'completed') {
                    clearInterval(interval);
                    let downloadUrl;
                    try {
                        // Replace the last occurrence of 'check-status/<id>' with 'download/<id>'
                        const u = new URL(effectiveStatusUrl, window.location.origin);
                        const parts = u.pathname.split('/');
                        const idx = parts.lastIndexOf('check-status');
                        if (idx !== -1) {
                            parts[idx] = 'download';
                            u.pathname = parts.join('/');
                            downloadUrl = u.toString();
                        }
                    } catch (_) {
                        downloadUrl = `/tools/download/${jobId}`; // fallback
                    }
                    const downloadRes = await fetch(downloadUrl);
                    const downloadData = await downloadRes.json();
                    downloadLink.innerHTML = 'Click here to download your file';
                    downloadLink.href = downloadData.download_url;
                }
            }, 1000);
        } catch (err) {
            console.error('Error during form submission:', err);
            showErrorPopup('Error during form submission: ' + err.message);
        }
    })
});


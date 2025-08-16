document.addEventListener("DOMContentLoaded", async () => {
    const viewer = document.getElementById("viewer");

    try {
        const response = await fetch("../");
        const text = await response.text();

        const folderRegex = /href="(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\//g;
        const folders = [];
        let match;
        while ((match = folderRegex.exec(text)) !== null) {
            folders.push(match[1]);
        }

        folders.sort().reverse();

        if (!folders.length) {
            viewer.innerHTML = "<p>No test run folders found.</p>";
            return;
        }

        const latest = folders[0];
        const base = `../${latest}`;
        const failed = await fetch(`${base}/failed/`).then(r => r.text());

        const imageRegex = /href="(.*?)_diff\.png"/g;
        const images = [];
        while ((match = imageRegex.exec(failed)) !== null) {
            images.push(match[1]);
        }

        if (!images.length) {
            viewer.innerHTML = "<p>No diffs found in the latest test run.</p>";
            return;
        }

        images.forEach(name => {
            const container = document.createElement("div");
            container.className = "viewer-item";
            container.innerHTML = `
                <h3>${name}</h3>
                <div style="display:flex;gap:10px;">
                    <div><strong>Baseline</strong><br><img src="${base}/baseline/${name}.png" alt="baseline"></div>
                    <div><strong>Current</strong><br><img src="${base}/current/${name}.png" alt="current"></div>
                    <div><strong>Diff</strong><br><img src="${base}/failed/${name}_diff.png" alt="diff"></div>
                </div>
                <button class="accept-btn" onclick="acceptAsBaseline('${name}', '${latest}')">Accept as Baseline</button>
            `;
            viewer.appendChild(container);
        });

    } catch (err) {
        console.error("❌ Viewer loading failed:", err);
        viewer.innerHTML = `<p style="color:red;">Error loading viewer: ${err.message}</p>`;
    }
});

function acceptAsBaseline(name, folder) {
    fetch(`/screenshot_viewer/accept_baseline?name=${name}&folder=${folder}`, { method: "POST" })
        .then(res => {
            if (res.ok) {
                alert(`✅ Accepted ${name} as baseline.`);
                location.reload();
            } else {
                alert(`❌ Failed to accept ${name} as baseline.`);
            }
        })
        .catch(err => {
            alert(`❌ Error: ${err}`);
        });
}

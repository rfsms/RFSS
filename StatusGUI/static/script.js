fetch('http://localhost:3000/data')
    .then(res => res.json())
    .then(data => {
        const ctx = document.getElementById('azelChart').getContext('2d');
        const azimuthData = data.map(entry => entry.az);
        const elevationData = data.map(entry => entry.el);
        const labels = data.map(entry => new Date(entry.time * 1000).toLocaleString());
        const latestEntry = data[data.length - 1];

        const serialNumberElement = document.getElementById('serialNumber');
        serialNumberElement.textContent = `Serial Number: ${latestEntry.serial}`;
        const gridIDelement = document.getElementById('gridID');
        gridIDelement.textContent = `Grid ID: ${latestEntry.grid}`;

        // Prepare data for schedChart
        const schedData = data.map(entry => entry.sched);
        const timeLabels = data.map(entry => {
            const date = new Date(entry.time * 1000);
            return `${date.getUTCFullYear()}-${date.getUTCMonth() + 1}-${date.getUTCDate()} ${date.getUTCHours()}:${date.getUTCMinutes()}`;
        });

        // Get context for schedChart
        const schedCtx = document.getElementById('schedChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Azimuth',
                    data: azimuthData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false
                },
                {
                    label: 'Elevation',
                    data: elevationData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Create schedChart
        new Chart(schedCtx, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [{
                    label: 'Sched',
                    data: schedData,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    x: {
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 1 // Adjust as needed
                        }
                    },
                    y: {
                        min: -1,
                        max: 1,
                        stepSize: 1,
                        beginAtZero: true
                    }
                }
            }
        });

    });

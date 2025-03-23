
    // Cricket Team Owner Statistics Dashboard

    // Load data
    const ownerData = {"Owner": ["Rohan", "Vikhyat", "Shreyansh", "Sai", "Ayush", "Adi", "Dhruv"], "Total Runs": [4, 10, 48, 71, 6, 30, 15], "Total Wickets": [0, 0, 0, 0, 0, 0, 0], "Player Count": [1, 2, 3, 6, 1, 1, 1]};
    const playerData = [{"Owner": "Rohan", "Player": "Quinton de Kock", "Team ID": 49, "Runs": 4, "Wickets": 0}, {"Owner": "Vikhyat", "Player": "Josh Hazlewood", "Team ID": 44, "Runs": 0, "Wickets": 0}, {"Owner": "Vikhyat", "Player": "Devdutt Padikkal", "Team ID": 44, "Runs": 10, "Wickets": 0}, {"Owner": "Shreyansh", "Player": "Sunil Narine", "Team ID": 46, "Runs": 44, "Wickets": 0}, {"Owner": "Shreyansh", "Player": "Andre Russell", "Team ID": 46, "Runs": 4, "Wickets": 0}, {"Owner": "Shreyansh", "Player": "Vaibhav Arora", "Team ID": 46, "Runs": 0, "Wickets": 0}, {"Owner": "Sai", "Player": "Yash Dayal", "Team ID": 43, "Runs": 0, "Wickets": 0}, {"Owner": "Sai", "Player": "Krunal Pandya", "Team ID": 43, "Runs": 0, "Wickets": 0}, {"Owner": "Sai", "Player": "Suyash Sharma", "Team ID": 43, "Runs": 0, "Wickets": 0}, {"Owner": "Sai", "Player": "Rinku Singh", "Team ID": 43, "Runs": 12, "Wickets": 0}, {"Owner": "Sai", "Player": "Virat Kohli", "Team ID": 43, "Runs": 59, "Wickets": 0}, {"Owner": "Sai", "Player": "Varun Chakaravarthy", "Team ID": 43, "Runs": 0, "Wickets": 0}, {"Owner": "Ayush", "Player": "Venkatesh Iyer", "Team ID": 50, "Runs": 6, "Wickets": 0}, {"Owner": "Adi", "Player": "Angkrish Raghuvanshi", "Team ID": 42, "Runs": 30, "Wickets": 0}, {"Owner": "Dhruv", "Player": "Liam Livingstone", "Team ID": 48, "Runs": 15, "Wickets": 0}];
    const ownerNames = ["Rohan", "Vikhyat", "Shreyansh", "Sai", "Ayush", "Adi", "Dhruv"];

    // Initialize after DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Create container elements
        const appDiv = document.createElement('div');
        document.getElementById('react-entry-point').innerHTML = '';
        document.getElementById('react-entry-point').appendChild(appDiv);
        
        // Add title
        const title = document.createElement('h1');
        title.textContent = 'Cricket Team Owner Statistics';
        appDiv.appendChild(title);
        
        // Create owner summary section
        const summarySection = document.createElement('div');
        const summaryTitle = document.createElement('h2');
        summaryTitle.textContent = 'Owner Performance Summary';
        summarySection.appendChild(summaryTitle);
        
        // Create owner table
        const ownerTable = document.createElement('table');
        ownerTable.className = 'dash-table';
        
        // Add header
        const tableHeader = document.createElement('thead');
        const headerRow = document.createElement('tr');
        Object.keys(ownerData).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        tableHeader.appendChild(headerRow);
        ownerTable.appendChild(tableHeader);
        
        // Add rows
        const tableBody = document.createElement('tbody');
        for (let i = 0; i < ownerData.Owner.length; i++) {
            const row = document.createElement('tr');
            Object.keys(ownerData).forEach(key => {
                const td = document.createElement('td');
                td.textContent = ownerData[key][i];
                row.appendChild(td);
            });
            tableBody.appendChild(row);
        }
        ownerTable.appendChild(tableBody);
        summarySection.appendChild(ownerTable);
        appDiv.appendChild(summarySection);
        
        // Create charts section
        const chartsSection = document.createElement('div');
        chartsSection.style.display = 'flex';
        chartsSection.style.justifyContent = 'space-between';
        
        // Create runs chart
        const runsChartDiv = document.createElement('div');
        runsChartDiv.style.width = '48%';
        const runsTitle = document.createElement('h2');
        runsTitle.textContent = 'Total Runs by Owner';
        runsChartDiv.appendChild(runsTitle);
        const runsChartContainer = document.createElement('div');
        runsChartContainer.id = 'runs-chart';
        runsChartContainer.className = 'dash-graph';
        runsChartDiv.appendChild(runsChartContainer);
        chartsSection.appendChild(runsChartDiv);
        
        // Create wickets chart
        const wicketsChartDiv = document.createElement('div');
        wicketsChartDiv.style.width = '48%';
        const wicketsTitle = document.createElement('h2');
        wicketsTitle.textContent = 'Total Wickets by Owner';
        wicketsChartDiv.appendChild(wicketsTitle);
        const wicketsChartContainer = document.createElement('div');
        wicketsChartContainer.id = 'wickets-chart';
        wicketsChartContainer.className = 'dash-graph';
        wicketsChartDiv.appendChild(wicketsChartContainer);
        chartsSection.appendChild(wicketsChartDiv);
        
        appDiv.appendChild(chartsSection);
        
        // Create player section
        const playerSection = document.createElement('div');
        const playerTitle = document.createElement('h2');
        playerTitle.textContent = 'All Players Data';
        playerSection.appendChild(playerTitle);
        
        // Create player table
        const playerTable = document.createElement('table');
        playerTable.className = 'dash-table';
        
        // Add header
        const playerTableHeader = document.createElement('thead');
        const playerHeaderRow = document.createElement('tr');
        Object.keys(playerData[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            playerHeaderRow.appendChild(th);
        });
        playerTableHeader.appendChild(playerHeaderRow);
        playerTable.appendChild(playerTableHeader);
        
        // Add rows
        const playerTableBody = document.createElement('tbody');
        playerData.forEach(player => {
            const row = document.createElement('tr');
            Object.keys(player).forEach(key => {
                const td = document.createElement('td');
                td.textContent = player[key];
                row.appendChild(td);
            });
            playerTableBody.appendChild(row);
        });
        playerTable.appendChild(playerTableBody);
        playerSection.appendChild(playerTable);
        appDiv.appendChild(playerSection);
        
        // Create player by owner section
        const playerByOwnerSection = document.createElement('div');
        const playerByOwnerTitle = document.createElement('h2');
        playerByOwnerTitle.textContent = 'Player Performance by Owner';
        playerByOwnerSection.appendChild(playerByOwnerTitle);
        
        // Create owner dropdown
        const dropdown = document.createElement('select');
        dropdown.id = 'owner-dropdown';
        dropdown.className = 'dash-dropdown';
        ownerNames.forEach(owner => {
            const option = document.createElement('option');
            option.value = owner;
            option.textContent = owner;
            dropdown.appendChild(option);
        });
        playerByOwnerSection.appendChild(dropdown);
        
        // Create chart container
        const ownerPlayersChartContainer = document.createElement('div');
        ownerPlayersChartContainer.id = 'owner-players-chart';
        ownerPlayersChartContainer.className = 'dash-graph';
        playerByOwnerSection.appendChild(ownerPlayersChartContainer);
        appDiv.appendChild(playerByOwnerSection);
        
        // Add footer
        const footer = document.createElement('div');
        const hr = document.createElement('hr');
        footer.appendChild(hr);
        const footerText = document.createElement('p');
        footerText.textContent = 'Cricket Team Owner Statistics Dashboard - Created with Plotly';
        footerText.style.textAlign = 'center';
        footer.appendChild(footerText);
        appDiv.appendChild(footer);
        
        // Initialize Plotly charts
        const runsData = [{
            x: ownerData.Owner,
            y: ownerData['Total Runs'],
            type: 'bar',
            marker: { color: 'rgba(55, 128, 191, 0.7)' }
        }];
        
        const wicketsData = [{
            x: ownerData.Owner,
            y: ownerData['Total Wickets'],
            type: 'bar',
            marker: { color: 'rgba(219, 64, 82, 0.7)' }
        }];
        
        const runsLayout = {
            title: 'Total Runs Scored by Each Owner\'s Players',
            xaxis: { title: 'Owner' },
            yaxis: { title: 'Total Runs' }
        };
        
        const wicketsLayout = {
            title: 'Total Wickets Taken by Each Owner\'s Players',
            xaxis: { title: 'Owner' },
            yaxis: { title: 'Total Wickets' }
        };
        
        Plotly.newPlot('runs-chart', runsData, runsLayout);
        Plotly.newPlot('wickets-chart', wicketsData, wicketsLayout);
        
        // Initialize player by owner chart
        function updateOwnerPlayersChart() {
            const selectedOwner = document.getElementById('owner-dropdown').value;
            const filteredPlayers = playerData.filter(player => player.Owner === selectedOwner);
            
            const chartData = [{
                x: filteredPlayers.map(p => p.Player),
                y: filteredPlayers.map(p => p.Runs),
                type: 'bar',
                marker: { color: 'rgba(55, 128, 191, 0.7)' }
            }];
            
            const chartLayout = {
                title: `Runs Scored by ${selectedOwner}'s Players`,
                xaxis: { title: 'Player' },
                yaxis: { title: 'Runs' }
            };
            
            Plotly.newPlot('owner-players-chart', chartData, chartLayout);
        }
        
        // Add event listener to dropdown
        document.getElementById('owner-dropdown').addEventListener('change', updateOwnerPlayersChart);
        
        // Initialize first chart
        updateOwnerPlayersChart();
    });
    
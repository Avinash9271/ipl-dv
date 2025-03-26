// Function to show all player names in the cricket dashboard
function showAllPlayers() {
  // Get all players and sort by score (descending), excluding players with 'Unknown' owner
  const players = Object.values(playerStats)
    .filter(player => player.owner !== 'Unknown')
    .sort((a, b) => b.score - a.score);
  
  // Print header
  console.log('===== CRICKET DASHBOARD PLAYER LIST =====');
  console.log(`Total Players: ${players.length}`);
  console.log('');
  
  // Create and print a table with detailed info
  console.table(players.map((player, index) => ({
    Rank: index + 1,
    Name: player.player_name,
    Owner: player.owner,
    Runs: player.runs,
    Wickets: player.wickets,
    Field: (player.catches || 0) + (player.stumpings || 0) + (player.run_outs || 0),
    Score: player.score.toFixed(1)
  })));
  
  // Print simple list with just names
  console.log('');
  console.log('===== PLAYER NAMES ONLY =====');
  players.forEach((player, index) => console.log(`${index+1}. ${player.player_name} (${player.owner})`));
  
  return players; // Return for further use if needed
}

// Instructions for use
console.log(`
To show all player names in the cricket dashboard:
1. Open your cricket dashboard in the browser
2. Open Developer Console (F12 or Ctrl+Shift+I or Cmd+Option+I on Mac)
3. Copy and paste this entire file into the console
4. Run the function by typing: showAllPlayers()
`);

// You can copy the entire content of this file, paste it in browser console,
// and then run the function. 
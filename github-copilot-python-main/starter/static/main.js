// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let timerInterval = null;
let startTime = null;
let elapsedSeconds = 0;
let gameCompleted = false;
let solution = [];
const LEADERBOARD_STORAGE_KEY = 'sudoku-leaderboard';
const THEME_STORAGE_KEY = 'sudoku-theme';

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, solvedBoard = []) {
  puzzle = puz;
  solution = solvedBoard;
  gameCompleted = false;
  resetTimer();
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `Time: ${minutes}:${seconds}`;
}

function updateTimerDisplay() {
  const timer = document.getElementById('timer');
  if (!timer) return;

  if (startTime === null) {
    timer.innerText = formatTime(elapsedSeconds);
    return;
  }

  const now = Date.now();
  const elapsed = Math.floor((now - startTime) / 1000) + elapsedSeconds;
  timer.innerText = formatTime(elapsed);
}

function resetTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  startTime = Date.now();
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerInterval = window.setInterval(updateTimerDisplay, 1000);
}

function pauseTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  if (startTime !== null) {
    elapsedSeconds += Math.floor((Date.now() - startTime) / 1000);
    startTime = null;
  }
  updateTimerDisplay();
}

function getLeaderboard() {
  const stored = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
  if (!stored) {
    return [];
  }

  try {
    return JSON.parse(stored);
  } catch (error) {
    return [];
  }
}

function saveLeaderboardEntry(name, timeSeconds, difficulty) {
  const leaderboard = getLeaderboard();
  leaderboard.push({name, timeSeconds, difficulty});
  leaderboard.sort((a, b) => a.timeSeconds - b.timeSeconds);
  const topTen = leaderboard.slice(0, 10);
  window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(topTen));
  renderLeaderboard();
}

function renderLeaderboard() {
  const list = document.getElementById('leaderboard-list');
  if (!list) return;

  const leaderboard = getLeaderboard();
  if (leaderboard.length === 0) {
    list.innerHTML = '<li>No scores yet.</li>';
    return;
  }

  list.innerHTML = leaderboard.map((entry, index) => {
    const minutes = Math.floor(entry.timeSeconds / 60).toString().padStart(2, '0');
    const seconds = (entry.timeSeconds % 60).toString().padStart(2, '0');
    return `<li>#${index + 1} ${entry.name} — ${minutes}:${seconds} — ${entry.difficulty}</li>`;
  }).join('');
}

function applyTheme(theme) {
  document.body.classList.toggle('dark', theme === 'dark');
  document.body.dataset.theme = theme;
  window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.innerText = theme === 'dark' ? 'Switch to Light Mode' : 'Toggle Dark Mode';
  }
}

function initializeTheme() {
  const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY) || 'light';
  applyTheme(savedTheme);
}

function resetCellStyles() {
  const boardDiv = document.getElementById('sudoku-board');
  if (!boardDiv) return;

  const inputs = boardDiv.getElementsByTagName('input');
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) {
      continue;
    }
    inp.className = 'sudoku-cell';
  }
}

function checkPuzzle() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  const incorrect = [];
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      if (board[i][j] !== 0 && board[i][j] !== solution[i][j]) {
        incorrect.push([i, j]);
      }
    }
  }

  resetCellStyles();
  for (const [row, col] of incorrect) {
    const idx = row * SIZE + col;
    const inp = inputs[idx];
    if (inp && !inp.disabled) {
      inp.className = 'sudoku-cell incorrect';
    }
  }

  const msg = document.getElementById('message');
  if (incorrect.length === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = 'No incorrect cells found.';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Incorrect cells highlighted in red.';
  }
}

function fillHint() {
  if (gameCompleted || solution.length === 0) {
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const emptyCells = [];

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      if (puzzle[i][j] === 0) {
        emptyCells.push({row: i, col: j, index: idx});
      }
    }
  }

  if (emptyCells.length === 0) {
    return;
  }

  const target = emptyCells[Math.floor(Math.random() * emptyCells.length)];
  puzzle[target.row][target.col] = solution[target.row][target.col];
  const input = inputs[target.index];
  input.value = solution[target.row][target.col];
  input.disabled = true;
  input.className = 'sudoku-cell prefilled';
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle, data.solution || []);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    gameCompleted = true;
    pauseTimer();
    const playerName = window.prompt('Enter your name for the leaderboard:', 'Player');
    if (playerName && playerName.trim()) {
      saveLeaderboardEntry(playerName.trim(), elapsedSeconds, document.getElementById('difficulty-select').value);
    }
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('check-puzzle').addEventListener('click', checkPuzzle);
  document.getElementById('hint-button').addEventListener('click', () => {
    fillHint();
  });
  document.getElementById('theme-toggle').addEventListener('click', () => {
    const nextTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  });
  initializeTheme();
  renderLeaderboard();
  // initialize
  newGame();
});
const { app, BrowserWindow, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow = null;
let streamlitProcess = null;
const STREAMLIT_PORT = 8501;

// Check if running in development
const isDev = process.argv.includes('--dev') || !app.isPackaged;

/**
 * Get the path to the Python app directory
 */
function getAppPath() {
  if (isDev) {
    return path.join(__dirname, '..', 'app');
  }
  return path.join(process.resourcesPath, 'app');
}

/**
 * Get the Python executable
 */
function getPythonPath() {
  // Try common Python paths
  const pythonPaths = [
    'python3',
    'python',
    '/usr/bin/python3',
    '/usr/local/bin/python3',
    // Add more paths for Windows if needed
  ];

  return pythonPaths[0]; // Default to python3
}

/**
 * Check if Streamlit is ready
 */
function checkStreamlitReady() {
  return new Promise((resolve) => {
    const check = () => {
      http.get(`http://localhost:${STREAMLIT_PORT}`, (res) => {
        resolve(true);
      }).on('error', () => {
        setTimeout(check, 500);
      });
    };
    check();
  });
}

/**
 * Start the Streamlit server
 */
async function startStreamlit() {
  const appPath = getAppPath();
  const mainPy = path.join(appPath, 'main.py');

  console.log('Starting Streamlit from:', mainPy);

  // Spawn Streamlit process
  streamlitProcess = spawn(getPythonPath(), [
    '-m', 'streamlit', 'run',
    mainPy,
    '--server.port', STREAMLIT_PORT.toString(),
    '--server.headless', 'true',
    '--browser.gatherUsageStats', 'false',
    '--server.address', 'localhost'
  ], {
    cwd: appPath,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: '1'
    }
  });

  // Log Streamlit output
  streamlitProcess.stdout.on('data', (data) => {
    console.log(`Streamlit: ${data}`);
  });

  streamlitProcess.stderr.on('data', (data) => {
    console.error(`Streamlit Error: ${data}`);
  });

  streamlitProcess.on('error', (error) => {
    console.error('Failed to start Streamlit:', error);
    dialog.showErrorBox(
      'Error Starting Application',
      `Could not start the Python backend.\n\nMake sure Python 3.8+ is installed and the required packages are available.\n\nError: ${error.message}`
    );
  });

  streamlitProcess.on('close', (code) => {
    console.log(`Streamlit process exited with code ${code}`);
    if (code !== 0 && mainWindow) {
      dialog.showErrorBox(
        'Application Error',
        `The Python backend has stopped unexpectedly (code ${code}).\n\nPlease restart the application.`
      );
    }
  });

  // Wait for Streamlit to be ready
  console.log('Waiting for Streamlit to start...');
  await checkStreamlitReady();
  console.log('Streamlit is ready!');
}

/**
 * Create the main application window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    title: 'Text Analysis AI Agent',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    },
    // macOS specific
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    trafficLightPosition: { x: 15, y: 15 }
  });

  // Load the Streamlit app
  mainWindow.loadURL(`http://localhost:${STREAMLIT_PORT}`);

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Stop the Streamlit process
 */
function stopStreamlit() {
  if (streamlitProcess) {
    console.log('Stopping Streamlit...');

    // Kill the process tree on Windows, just the process on Unix
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', streamlitProcess.pid, '/f', '/t']);
    } else {
      streamlitProcess.kill('SIGTERM');
    }

    streamlitProcess = null;
  }
}

// App lifecycle events
app.whenReady().then(async () => {
  try {
    await startStreamlit();
    createWindow();
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox('Startup Error', error.message);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopStreamlit();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopStreamlit();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  dialog.showErrorBox('Error', error.message);
});

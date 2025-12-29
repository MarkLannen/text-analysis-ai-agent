/**
 * Preload script for Electron
 * Exposes safe APIs to the renderer process
 */
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // Platform info
  getPlatform: () => process.platform,

  // Window controls
  minimizeWindow: () => ipcRenderer.send('minimize-window'),
  maximizeWindow: () => ipcRenderer.send('maximize-window'),
  closeWindow: () => ipcRenderer.send('close-window'),

  // Screenshot (if we need native screenshot capabilities)
  captureScreen: () => ipcRenderer.invoke('capture-screen'),

  // File dialogs
  openFile: (options) => ipcRenderer.invoke('open-file-dialog', options),
  saveFile: (options) => ipcRenderer.invoke('save-file-dialog', options),

  // Notifications
  showNotification: (title, body) => ipcRenderer.send('show-notification', { title, body })
});

// Log when preload script loads
console.log('Preload script loaded');

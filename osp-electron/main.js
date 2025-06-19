const { app, BrowserWindow } = require('electron')
const path = require('path')

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // Carga la app web local
  win.loadURL('http://localhost:5173')
}

app.whenReady().then(() => {
  createWindow()
})
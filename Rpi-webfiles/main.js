let {PythonShell} = require('python-shell');
const {app, BrowserWindow} = require('electron');
const process = require('child_process');

function createWindow() {
    window = new BrowserWindow({width: 500, height: 500});
    window.loadFile("node_index.html");
    PythonShell.run('./app.py', function (err, result) {
        if (err) console.log(err);
        console.log(result);
    });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
        process.exec("pkill -9 py")
    }
});

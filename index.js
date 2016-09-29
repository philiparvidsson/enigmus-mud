var conn = new WebSocket('ws://127.0.0.1:1337')

conn.onerror = (err) => {
    console.log('err', err)
}

conn.onmessage = (e)  => {
    s = e.data

    //s = s.replace(/(?:\r\n|\r|\n)/g, '<br/>')

    document.getElementById('text').innerHTML += s
}

conn.onopen = () => {
    console.log('heylo connected')
    conn.send('heylo\n')
}

function sendCommand(s) {
    conn.send(s + '\n')
}

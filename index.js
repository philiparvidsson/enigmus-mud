var conn = new WebSocket('ws://127.0.0.1:1337')

conn.onerror = (err) => {
    console.log('err', err)
}

conn.onmessage = (e)  => {
    s = e.data

    //s = s.replace(/(?:\r\n|\r|\n)/g, '<br/>')

    textElem = document.getElementById('text')
    textElem.innerHTML += s
    textElem.scrollTop = textElem.scrollHeight;
}

conn.onopen = () => {
}

function sendCommand(s) {
    textElem.innerHTML += s + '\n'
    conn.send(s + '\n')
}

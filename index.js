var conn = new WebSocket('ws://127.0.0.1:1337')

conn.onerror = (err) => {
    console.log('err', err)
}

conn.onmessage = (e)  => {
    console.log('msg', e.data)
}

conn.onopen = () => {
    console.log('heylo connected')
    conn.send('heylo')
}

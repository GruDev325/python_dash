window.onload = function () {
    // console.log('entered window.onload()')
    if(window.innerWidth <= 500) {
        var mvp = document.getElementById('myViewport');
        // var tick = document.getElementById('tick');
        // console.log('tick value = ' + tick)

        mvp.setAttribute('screen', window.innerWidth);
        // console.log('width = ' + window.innerWidth)
    }
}
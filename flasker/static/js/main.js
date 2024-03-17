
// show display message
function show(message, sucesss) {
    let msg_box = document.getElementById("msg");

    if (message) {
        msg_box.classList.remove("fade");

        if (sucesss == "success") {
            msg_box.classList.add("flash-success");
        }else if (sucesss == "info") {
            msg_box.classList.add("flash-info");
        }
    }
    else if (!message) {
        msg_box.classList.add("fade");
    }
    
}

// fade display message
function fade() {
    let msg_box = document.getElementById("msg");
    
    msg_box.classList.add("fade");
}
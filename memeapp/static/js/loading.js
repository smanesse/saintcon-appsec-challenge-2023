// this file is out-of-scope for vulnerabilities

function showLoading() {
    document.getElementById("loading").classList.remove("hideLoading")
    document.getElementById("loading").classList.add("showLoading")
}

function hideLoading() {
    document.getElementById("loading").classList.add("hideLoading")
    document.getElementById("loading").classList.remove("showLoading")
}

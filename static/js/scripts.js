// Footer Get Current Year
document.getElementById("year").innerHTML = new Date().getFullYear()

// Footer Fixed Bottom
function check_title() {
    const title = document.getElementsByTagName("title")[0].textContent
    if (title == " Sulat Aian - Sign In " || title == " Sulat Aian - Sign Up " || title == " Sulat Aian - Contact ") {
        const footer = document.getElementById("footer")
        footer.style.display = "none"
    }
}

check_title();
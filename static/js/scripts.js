// Footer Get Current Year
document.getElementById("year").innerHTML = new Date().getFullYear()

// Footer Fixed Bottom
function check_title() {
    const title = document.getElementsByTagName("title")[0].textContent
    const footer_hr = document.getElementById("footer-hr")
    if (title == " Sulat Aian - Sign In " || title == " Sulat Aian - Sign Up ") {
        const footer = document.getElementById("footer")
        footer.style.position = "fixed"
        footer.style.left = 0
        footer.style.right = 0
        footer.style.bottom = 0 
        footer_hr.style.display = "none"
    }
}

check_title();
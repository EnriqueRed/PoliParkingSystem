function get_username() {
    var email = document.getElementById("email").value
    document.getElementById("username").value = email.substring(0, email.search("@poligran.edu.co"));
}

// function deleteSomething(id) {
//     fetch("/delete-something", {
//         method: "POST",
//         BODY: JSON.stringify({ id: id }),
//     }).then((_res) => {
//         window.location.href = "/";
//     });
// }